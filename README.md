# GDEX Freva Deployment
This repository contains an initial test setup for deploying Freva on the
NCAR Kubernetes environment.
It serves as a proof of concept to explore and refine the future deployment
approach.


## Repository Structure
All Kubernetes manifests are located in the `freva/`
directory.
Note that the current secrets have been auto-generated — this is a
temporary solution, and a more robust secret management approach will be
introduced later.

## Manifest Generation

The manifests were generated using the
[deploy-freva python pacakge](https://github.com/freva-org/freva-admin/tree/kubernetes)
Python package.

To install the `kubernetes` branch, run:

```console
python3 -m pip install git+https://github.com/freva-org/freva-admin.git@kubernetes
```

Once installed, you can create the manifests with:

```console
deploy-freva kubernetes -c freva-ncar.toml -o freva
```

## Notes

- The `freva-ncar.toml` configuration file defines the deployment parameters.
- The generated manifests under freva/ *could* be applied directly to a
  Kubernetes cluster using `kubectl apply -f freva/`.
- Future iterations will improve secret handling, configuration templating, and Helm integration.
