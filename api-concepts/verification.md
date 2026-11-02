| Viewpoint | Tool / Evidence Source | Key Confirmed Data | Status |

| :--- | :--- | :--- | :--- |

| **1. DNS Resolution** | `nslookup jsonplaceholder.typicode.com` | `172.67.167.151`, `104.21.59.19` | PASS | DONE

| **2. Browser View** | Chrome `/posts/1` (Pretty-print) | JSON `userId: 1, id: 1` | PASS | DONE

| **3. Network Capture** | Chrome DevTools Network Waterfall | `1` (`200`, `document`, `0.9 kB`, `18 ms`) | PASS | DONE

| **4. Request General** | DevTools -> Headers -> General | `GET`, `200 OK`, `172.67.167.151:443` | PASS | DONE

| **5. Response Headers** | DevTools -> Headers -> Response | `application/json; charset=utf-8`, `HIT` | PASS | DONE

| **6. Response Body** | DevTools -> Response Tab | 6-line JSON object matching browser | PASS | DONE

| **7. CLI + Headers** | `curl -i .../posts/1` | `HTTP/2 200` + Cloudflare headers + JSON | PASS | DONE

| **8. CLI Clean JSON** | `curl -s .../posts/1` | Clean JSON payload on stdout | PASS | DONE