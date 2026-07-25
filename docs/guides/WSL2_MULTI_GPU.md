# WSL2 multi-GPU (NVIDIA) — PyTorch sees all GPUs

Use this when `nvidia-smi -L` lists multiple GPUs but `torch.cuda.device_count()` is `1` (often only the primary GPU is exposed to CUDA in WSL).

## 1. Windows `.wslconfig`

Path: `C:\Users\<username>\.wslconfig`

Content:

```ini
[wsl2]
gpus=all
kernelCommandLine=nvidia.NVreg_EnableGpuFirmware=0
```

From WSL, if `cmd.exe` is on PATH, or use:

`/mnt/c/Windows/System32/cmd.exe /c "..."`

**Note:** If CMD reports a UNC current directory error, run the command from a **Windows** terminal (PowerShell/cmd) or `cd /mnt/c/Users/<you>` first so the current directory is a drive letter path.

## 2. Full WSL shutdown

From **PowerShell or cmd on Windows** (not only inside WSL):

```powershell
wsl --shutdown
```

Re-open WSL after a few seconds.

## 3. Verify

```bash
nvidia-smi -L
python3 -c "import torch; print('GPU count:', torch.cuda.device_count()); [print(i, torch.cuda.get_device_name(i), torch.cuda.get_device_capability(i)) for i in range(torch.cuda.device_count())]"
```

Expect two lines for two GPUs, e.g. `(6, 1)` for Pascal and `(8, 6)` for Ampere.

## 4. Pin RTX 3090 for FAITHH

Repo default in `faithh_professional_backend_fixed.py` uses `CUDA_VISIBLE_DEVICES=1` when unset (3090 as second GPU). To make it explicit:

- Set `CUDA_VISIBLE_DEVICES=1` in `~/ai-stack/.env`
- `./restart_backend.sh` **sources `.env`** before starting the backend

Or one-shot:

```bash
CUDA_VISIBLE_DEVICES=1 ./restart_backend.sh
```

## 5. Smoke checks

```bash
curl -s http://127.0.0.1:5557/api/plc/state | python3 -m json.tool | head -15
curl -s http://127.0.0.1:5557/api/usage
curl -s http://127.0.0.1:5557/api/health | python3 -m json.tool | head -10
```
