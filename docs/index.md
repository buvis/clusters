# Bob's Universal and Very Intelligent System
This is the documentation for my home Kubernetes clusters in a declarative state. [Flux](https://github.com/fluxcd/flux2) watches my [clusters repository](https://github.com/buvis-net/clusters) and makes the changes to them based on the YAML manifests.

A lot of inspiration for my cluster came from the people that have shared their clusters over at [awesome-home-kubernetes](https://github.com/k8s-at-home/awesome-home-kubernetes).

Another important component of BUVIS as a system are my [dotfiles, scripts and other artifacts](https://github.com/tbouska/buvis).


## Hardware

### Specifications

| Device   | Role    | Model                          | CPU                         | RAM  | /dev/sda                        | /dev/sdb                        |
|----------|---------|--------------------------------|-----------------------------|------|---------------------------------|---------------------------------|
| hawking  | worker  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 8 GB | SanDisk Ultra Fit USB 3.1 256GB | SanDisk Ultra Fit USB 3.1 256GB |
| columbus | master  | Raspberry Pi 4 Model B Rev 1.1 | ARMv8 Processor rev 3 (v8l) | 4 GB |                                 |                                 |
| braun    | worker  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 8 GB | SanDisk Ultra Fit USB 3.1 256GB | SanDisk Ultra Fit USB 3.1 256GB |
| hertz    | worker  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 4 GB | SanDisk Ultra Fit USB 3.1 256GB | SanDisk Ultra Fit USB 3.1 256GB |
| feynman  | worker  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 8 GB | SanDisk Ultra Fit USB 3.1 256GB | SanDisk Ultra Fit USB 3.1 256GB |
| nimitz   | master  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 4 GB |                                 |                                 |
| planck   | worker  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 8 GB | SanDisk Ultra Fit USB 3.1 256GB | SanDisk Ultra Fit USB 3.1 256GB |
| einstein | worker  | Raspberry Pi 4 Model B Rev 1.4 | ARMv8 Processor rev 3 (v8l) | 4 GB | SanDisk Ultra Fit USB 3.1 256GB | SanDisk Ultra Fit USB 3.1 256GB |
| kao      | proxmox | Intel NUC                      |                             |      |                                 |                                 |

### Physical layout

|          |         |          |         |
|----------|---------|----------|---------|
| feynman  |         | hawking  |         |
| nimitz   |         | columbus |         |
| planck   |         | braun    |         |
| einstein | _orcus_ | hertz    | _domum_ |
