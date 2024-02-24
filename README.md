# video-splitter

Run with `./cli INPUT_FILE CFG.YAML [--output OUTPUT_DIRECTORY]`

## Config file format

A few options, but only one is tested thoroughly at all:

```yaml
section-name-1:
    start: 1m 2s
    end: 5m 4s
```

Start and end timestamps are pretty flexile (case insensitive, add a comma, be free).

