from .base_collector import BaseCollector
import requests
import time


class HealthCollector(BaseCollector):
    name = "health"  # Output: health.json

    SERVICES = {
        "faithh_backend": {
            "url": "http://localhost:5557/health",
            "type": "http",
        },
        "ollama": {
            "url": "http://localhost:11434/api/tags",
            "type": "http",
        },
        "chromadb_gen8": {
            "url": "http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat",
            "type": "chromadb",
            "expected_docs": 29013,
            "collection": "faithh_knowledge_base",
            "tenant": "default_tenant",
            "database": "default_database",
        },
    }

    def collect(self) -> dict:
        services = {}
        issues = []

        for name, config in self.SERVICES.items():
            result = self._check_service(name, config)
            services[name] = result

            if result["status"] != "healthy":
                issues.append(self._create_issue(name, result))

        return {
            "overall_status": self._compute_overall(services),
            "services": services,
            "issues": issues,
        }

    def _check_service(self, name: str, config: dict) -> dict:
        url = config["url"]
        result = {
            "url": url,
            "status": "unknown",
            "response_time_ms": 0,
        }

        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            result["response_time_ms"] = int((time.time() - start) * 1000)

            if response.status_code == 200:
                result["status"] = "healthy"
                data = response.json()

                if name == "faithh_backend":
                    result["version"] = data.get("service", "").split()[-1]

                elif name == "ollama":
                    models = [m.get("name") for m in data.get("models", [])]
                    result["models"] = models

                elif name == "chromadb_gen8":
                    result["reachable"] = True
                    expected_docs = config.get("expected_docs")
                    if expected_docs is not None:
                        result["expected_documents"] = expected_docs
                    collection_name = config.get("collection", "faithh_knowledge_base")
                    result["collection"] = collection_name
                    base_url = config.get("base_url")
                    if not base_url:
                        if "/api/" in url:
                            base_url = url.split("/api/")[0]
                        elif "/v2/" in url:
                            base_url = url.split("/v2/")[0]
                        else:
                            base_url = url.rsplit("/", 1)[0]
                    base_url = base_url.rstrip("/")
                    result["base_url"] = base_url
                    tenant = config.get("tenant", "default_tenant")
                    database = config.get("database", "default_database")
                    result["tenant"] = tenant
                    result["database"] = database

                    try:
                        collections = None
                        collection_url = None
                        last_error_status = None
                        for endpoint in (
                            f"{base_url}/api/v2/tenants/{tenant}/databases/{database}/collections",
                            f"{base_url}/v2/tenants/{tenant}/databases/{database}/collections",
                            f"{base_url}/api/v2/collections",
                            f"{base_url}/v2/collections",
                            f"{base_url}/api/v1/collections",
                            f"{base_url}/v1/collections",
                        ):
                            resp = requests.get(endpoint, timeout=5)
                            if resp.status_code in (400, 404, 410):
                                if resp.status_code == 400:
                                    last_error_status = 400
                                continue
                            if resp.status_code != 200:
                                result["connected"] = False
                                result["status"] = "degraded"
                                result["issue"] = f"HTTP {resp.status_code}"
                                return result
                            payload = resp.json()
                            if isinstance(payload, dict) and "collections" in payload:
                                collections = payload["collections"]
                            elif isinstance(payload, list):
                                collections = payload
                            collection_url = endpoint
                            break

                        if collections is not None:
                            result["collections_endpoint"] = collection_url
                            for coll in collections:
                                if coll.get("name") == collection_name:
                                    result["connected"] = True
                                    count = coll.get("count")
                                    if count is None:
                                        count = coll.get("size")
                                    result["documents"] = count if count is not None else "unknown"
                                    break
                            else:
                                result["connected"] = False
                                result["documents"] = 0
                                result["status"] = "degraded"
                                result["issue"] = "Collection not found"
                        else:
                            direct_endpoints = (
                                f"{base_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{collection_name}",
                                f"{base_url}/v2/tenants/{tenant}/databases/{database}/collections/{collection_name}",
                                f"{base_url}/api/v2/collections/{collection_name}",
                                f"{base_url}/v2/collections/{collection_name}",
                                f"{base_url}/api/v1/collections/{collection_name}",
                                f"{base_url}/v1/collections/{collection_name}",
                            )
                            direct_resp = None
                            for endpoint in direct_endpoints:
                                direct_resp = requests.get(endpoint, timeout=5)
                                if direct_resp.status_code in (400, 404, 410):
                                    if direct_resp.status_code == 400:
                                        last_error_status = 400
                                    continue
                                if direct_resp.status_code != 200:
                                    result["connected"] = False
                                    result["status"] = "degraded"
                                    result["issue"] = f"HTTP {direct_resp.status_code}"
                                    return result
                                payload = direct_resp.json()
                                result["connected"] = True
                                count = payload.get("count") if isinstance(payload, dict) else None
                                if count is None and isinstance(payload, dict):
                                    count = payload.get("size")
                                if count is None:
                                    count_resp = requests.get(f"{endpoint}/count", timeout=5)
                                    if count_resp.status_code == 200:
                                        count_payload = count_resp.json()
                                        if isinstance(count_payload, dict):
                                            count = count_payload.get("count")
                                        elif isinstance(count_payload, int):
                                            count = count_payload
                                result["documents"] = count if count is not None else "unknown"
                                break

                            if result.get("connected") is not True:
                                result["connected"] = False
                                result["status"] = "degraded"
                                if last_error_status:
                                    result["issue"] = f"Collections endpoint unavailable (HTTP {last_error_status})"
                                else:
                                    result["issue"] = "Collections endpoint unavailable"
                    except Exception as exc:
                        result["connected"] = False
                        result["status"] = "degraded"
                        result["issue"] = str(exc)
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = "Connection timed out"
        except requests.exceptions.ConnectionError:
            result["status"] = "unreachable"
            result["error"] = "Connection refused"
        except Exception as exc:
            result["status"] = "error"
            result["error"] = str(exc)

        return result

    def _compute_overall(self, services: dict) -> str:
        statuses = [service["status"] for service in services.values()]
        if all(status == "healthy" for status in statuses):
            return "healthy"
        if any(status in ["unreachable", "error"] for status in statuses):
            return "critical"
        return "degraded"

    def _create_issue(self, name: str, result: dict) -> dict:
        return {
            "service": name,
            "severity": "high" if result["status"] in ["unreachable", "error"] else "medium",
            "message": result.get("issue")
            or result.get("error")
            or f"Status: {result['status']}",
            "suggested_action": self._suggest_action(name, result),
        }

    def _suggest_action(self, name: str, result: dict) -> str:
        if result["status"] == "unreachable":
            return f"Check if {name} service is running"
        if name == "chromadb_gen8" and result.get("status") == "degraded":
            return "Check collection name matches 'faithh_knowledge_base'"
        return "Investigate service logs"
