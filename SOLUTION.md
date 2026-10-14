# Lab 6: REST and gRPC

| Method | Local | Same-Zone | Different Region |
|---|---:|---:|---:|
| REST add | 2.704 | 3.048 | 354.286 |
| gRPC add | 0.982 | 1.247 | 160.314 |
| REST rawimage | 5.016 | 7.207 | 1424.157 |
| gRPC rawimage | 8.466 | 8.755 | 188.162 |
| REST dotproduct | 3.714 | 3.664 | 332.831 |
| gRPC dotproduct | 0.993 | 1.457 | 161.727 |
| REST jsonimage | 32.100 | 32.124 | 1504.887 |
| gRPC jsonimage | 23.450 | 19.544 | 202.741 |
| PING | 0.050 | 0.422 | 141.126 |

(Values in ms)

gRPC was faster for addition and dot products in all three setups, with the largest advantage across regions. Cross-region addition took 354.286 ms with REST and 160.314 ms with gRPC, compared with a ping round-trip time of 141.126 ms. This is consistent with REST opening a new TCP connection for each request while gRPC reused one connection, reducing the effect of network latency. REST was faster for raw images locally and within the same zone, but gRPC was much faster across regions. JSON images were slower than raw images for both protocols because base64 increases the payload size by one third and requires decoding.
