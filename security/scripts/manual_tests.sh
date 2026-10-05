#!/usr/bin/env bash
# Pruebas manuales contra la API local (solo 127.0.0.1)
B=${1:-http://127.0.0.1:8000}
c(){ curl -s --path-as-is -o /tmp/_b -w "%{http_code}" "$@"; }
echo "== Metodos en /api/clima"; for m in POST PUT DELETE PATCH OPTIONS TRACE; do echo "$m $(c -X $m $B/api/clima) $(head -c 80 /tmp/_b)"; done
echo "== Traversal / archivos sensibles"
for p in /../../etc/passwd /%2e%2e/%2e%2e/etc/passwd /..%2f..%2fetc/passwd //etc/passwd /assets/../../backend/app/main.py /.env /.git/config /assets/x.js.map /backend/requirements.txt /%00 /api/../api/clima /api/clima/ "/api/clima?x=%3Cscript%3E"; do echo "$p -> $(c "$B$p") $(head -c 60 /tmp/_b|tr '\n' ' ')"; done
echo "== CORS"
for o in http://localhost:5173 http://evil.example null; do echo "Origin $o:"; curl -s -D- -o /dev/null -H "Origin: $o" $B/api/clima | grep -i '^access-control\|^vary'; done
echo "preflight:"; curl -s -D- -o /dev/null -X OPTIONS -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: x-evil" $B/api/clima | grep -i '^HTTP\|^access-control'
echo "== Cabeceras por tipo de respuesta"
for p in /api/clima /nope /docs /; do echo "-- $p"; curl -s -D- -o /dev/null $B$p | grep -i '^HTTP\|content-security\|cache-control\|x-frame\|nosniff\|server'; done
echo "== Host falso / cabeceras gigantes"
echo "host: $(c -H 'Host: evil.example' $B/api/clima)"; echo "bighdr: $(c -H "X-A: $(head -c 70000 /dev/zero|tr '\0' a)" $B/api/clima)"
echo "== /docs bajo CSP"; curl -s $B/docs | grep -o 'https://[^"]*' | sort -u
