import * as http from 'http';
import * as https from 'https';

export interface ChatResponse {
    success: boolean;
    response: string;
    model_used: string;
    provider: string;
    response_time: number;
    rag_used: boolean;
    ml_chips_activated?: Array<{ id: string; label: string; score: number }>;
    integrations_used?: string[];
    error?: string;
}

export interface HealthResponse {
    status: string;
    features: string[];
}

export interface PulseState {
    success: boolean;
    avatar: {
        mood: string;
        energy: number;
        alerts: string[];
        suggestions: string[];
        alert_count: number;
    };
    stale: boolean;
    state_age_minutes?: number;
}

export class BackendClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    private request(path: string, options?: { method?: string; body?: string }): Promise<string> {
        return new Promise((resolve, reject) => {
            const url = new URL(this.baseUrl + path);
            const isHttps = url.protocol === 'https:';
            const lib = isHttps ? https : http;

            const req = lib.request(
                {
                    hostname: url.hostname,
                    port: url.port,
                    path: url.pathname,
                    method: options?.method || 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(options?.body ? { 'Content-Length': Buffer.byteLength(options.body) } : {})
                    },
                    timeout: 120000
                },
                (res) => {
                    let data = '';
                    res.on('data', (chunk: string) => { data += chunk; });
                    res.on('end', () => resolve(data));
                }
            );

            req.on('error', reject);
            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timed out'));
            });

            if (options?.body) {
                req.write(options.body);
            }
            req.end();
        });
    }

    async checkHealth(): Promise<boolean> {
        try {
            const raw = await this.request('/health');
            const data = JSON.parse(raw) as HealthResponse;
            return !!data.status || !!data.features;
        } catch {
            return false;
        }
    }

    async chat(message: string, model: string, useRag: boolean = true, provider?: string): Promise<ChatResponse> {
        const body: Record<string, unknown> = { message, use_rag: useRag };
        if (model) {
            body.model = model;
        }
        if (provider) {
            body.provider = provider;
        }

        const raw = await this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify(body)
        });

        return JSON.parse(raw) as ChatResponse;
    }

    async getStatus(): Promise<Record<string, unknown>> {
        const raw = await this.request('/api/status');
        return JSON.parse(raw);
    }

    async getMlChips(): Promise<unknown[]> {
        const raw = await this.request('/api/ml/chips');
        const data = JSON.parse(raw);
        return data.chips || [];
    }

    async getPulseState(): Promise<PulseState> {
        const raw = await this.request('/api/pulse/state');
        return JSON.parse(raw) as PulseState;
    }

    async getJournal(date?: string): Promise<Record<string, unknown>> {
        const path = date ? `/api/journal?date=${date}` : '/api/journal';
        const raw = await this.request(path);
        return JSON.parse(raw);
    }
}
