# PhyResLib: scientific instrument automation framework

# About `phyreslib`

Welcome to physics research library (`phyreslib` or `prl`)! Based on research experience in a condensed matter physics laboratory, `prl` is designed to be a Pythonic system-desgin platform and development environment for scientific experiments invloving instrument automation, data acquisition, data visualization, and more.

# Getting started with `phyreslib`

1. Setup virtual environment for `prl` and install dependent packages. It is recommended to run `prl` in a virtual environment. Here we use `Enthought Deployment Manager (EDM)`.
```
[~]$ edm envs create prl-env
[~]$ edm shell -e prl-env
(prl-env) [~]$ edm install traits traitsui chaco pyside numpy
```

2. Checkout the appropriate branch on `phyreslib`.
```
(prl-env)[~]$ mkdir ~/prl-demo
(prl-env)[~]$ cd ~/prl-demo
(prl-env)[~/prl-demo]$ git clone https://github.com/OrbitSoft/phyreslib
(prl-env) [~/prl-demo]$ cd ~/prl-demo/phyreslib/
(prl-env) [~/prl-demo/phyreslib]$ git checkout master
```

3. Run some examples to get a taste of `prl`.
```
(prl-env) [~/prl-demo/phyreslib]$ cd ..
(prl-env) [~/prl-demo]$ python -m phyreslib.examples.scan_image
```
