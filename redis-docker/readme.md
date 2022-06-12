

```
podman build -t redis .
podman run -d -it --name redis -p 6379:6379 redis
```
