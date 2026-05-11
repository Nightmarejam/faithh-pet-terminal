# Security Snapshot — 20260402_140958

## Gen8 fail2ban
fail2ban-client: unavailable

## Gen8 UFW
sudo: a password is required
UFW: sudo password required or ufw unavailable

## NAS listening ports
tcp        0      0 0.0.0.0:139             0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:65368           0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:33304         0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:445             0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:161           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:6690            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5001            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5001            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5001            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:5001            0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::139                  :::*                    LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
tcp6       0      0 :::443                  :::*                    LISTEN      -                   
tcp6       0      0 :::443                  :::*                    LISTEN      -                   
tcp6       0      0 :::443                  :::*                    LISTEN      -                   
tcp6       0      0 :::443                  :::*                    LISTEN      -                   
tcp6       0      0 :::445                  :::*                    LISTEN      -                   
tcp6       0      0 :::3261                 :::*                    LISTEN      -                   
tcp6       0      0 :::3263                 :::*                    LISTEN      -                   
tcp6       0      0 :::3264                 :::*                    LISTEN      -                   
tcp6       0      0 :::6690                 :::*                    LISTEN      -                   
tcp6       0      0 :::5000                 :::*                    LISTEN      -                   
tcp6       0      0 :::5000                 :::*                    LISTEN      -                   
tcp6       0      0 :::5000                 :::*                    LISTEN      -                   
tcp6       0      0 :::5000                 :::*                    LISTEN      -                   
tcp6       0      0 :::5001                 :::*                    LISTEN      -                   
tcp6       0      0 :::5001                 :::*                    LISTEN      -                   
tcp6       0      0 :::5001                 :::*                    LISTEN      -                   
tcp6       0      0 :::5001                 :::*                    LISTEN      -                   

## NAS shell users
admin:x:1024:100:System default user:/var/services/homes/admin:/bin/sh
daemon:x:2:2::/:/bin/sh
lp:x:7:7::/var/spool/lpd:/bin/sh
Nightmarejam:x:1026:100::/var/services/homes/Nightmarejam:/bin/sh
postgres:x:55:55::/var/services/pgsql:/bin/sh
root:x:0:0::/root:/bin/ash

## Active Prometheus alerts
1 alerts firing
  ChromaDBDown

## ChromaDB
/api/v2/heartbeat: {"nanosecond heartbeat":1775164200402613586}

Snapshot complete: /home/jonat/ai-stack/reports/security/security_snapshot_20260402_140958.md
