# Edge Server Placement

## Problem Formulatiom

### Mobile Edge Environment

![](resources/example-mec.png)

Edge server placement problem can be considered as a network. which is an undirected graph $G = (V, E)$, where

- $V = B \cup S$
  - $B$: the set of **Base stations**
  - $S$: the set of **Edge servers**

- $E$
  - **The links between base stations and edge servers**
  - The links between base stations and mobile users
  - The links between base stations

## Dataset

The default dataset is the preprocessed and simplified version of [The Telecom Dataset](http://sguangwang.com/TelecomDataset.html), provided by Shanghai Telecom, and you can expand the dataset size by downloading all data from [there](http://sguangwang.com/TelecomDataset.html).

## Reference

| Author                 | Paper                                          | Publication | Year |
| ---------------------- | ---------------------------------------------- | ----------- | ---- |
| Yuanzhe Li et al.      | Profit-aware Edge Server Placement             | IoTJ        | 2021 |
| Shangguang Wang et al. | Edge server placement in mobile edge computing | JPDS        | 2019 |
