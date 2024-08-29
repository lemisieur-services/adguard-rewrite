# AdGuard Home DNS Rewrite Action

## Description

This action allows you to manage DNS rewrites in your AdGuard Home instance by providing a JSON file with the desired DNS entries.

The idea is to have a JSON file in your repository with the desired DNS rewrites and use this action to ensure that the DNS rewrites in your AdGuard Home instance match the entries specified in the JSON file. This way, you can manage your DNS rewrites in a version-controlled way, and changes can now be reviewed, audited and deployed to multiple servers at once.

### Features

- Manage DNS rewrites in your AdGuard Home instance using a JSON file.
- Version control your DNS rewrites.
- Automate the deployment of DNS rewrites to multiple AdGuard Home instances.

## Inputs

> [!CAUTION]
> Even if we are masking both `ADGUARD_USERNAME` and `ADGUARD_PASSWORD` inputs in the logs, it is recommended to use GitHub Secrets to store these values.
>
> Never commit any sensitive information to your repository.

- `DNS_FILE` (required): Path to the file (JSON) containing the DNS rewrites.
- `ADGUARD_USERNAME` (required): Username for your AdGuard instance.
- `ADGUARD_PASSWORD` (required): Password for your AdGuard instance.
- `ADGUARD_URL` (required): URL for your AdGuard instance (http(s)://my.instance:443). Must be accessible from your GitHub Actions runner.

## Usage

### JSON file format

We're expecting a JSON file with an array of objects, each object representing a DNS rewrite. The object should have two keys: `domain` and `answer`. The `domain` key should contain the domain you want to rewrite, and the `answer` key should contain the IP address you want to rewrite the domain to.
The tldr; is that you can specify a domain and an IP address to rewrite it to, pretty much how the AdGuard Home API is returning the values.

```json
[
  { "domain": "sub1.mydomain.com", "answer": "192.168.2.156" },
  { "domain": "*.sub1.mydomain.com", "answer": "10.1.1.4" },
  { "domain": "google.com", "answer": "172.168.3.67" }
]
```

### Example workflow

Here is an example of how to use this action in your workflow:

> [!TIP]
> You can find more examples in the [.examples](./.examples) directory, including a multi-instance deployment example.

```yaml
name: Update AdGuard DNS Rewrites

on:
  push:
    paths:
      - "dns_rewrites.json"

jobs:
  update-dns:
    runs-on: self-hosted # Should have network access to your AdGuard instance
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Update AdGuard DNS Rewrites
        uses: lemisieur-services/adguard-rewrite@v1
        with:
          DNS_FILE: dns_rewrites.json
          ADGUARD_USERNAME: ${{ secrets.ADGUARD_USERNAME }}
          ADGUARD_PASSWORD: ${{ secrets.ADGUARD_PASSWORD }}
          ADGUARD_URL: https://my.adguard.instance:443
```

## Getting Help

If you need help or have any questions, feel free to open an [issue](https://github.com/lemisieur-services/adguard-rewrite/issues/new) in the GitHub repository to get in touch.
