# 3. Title: Topology-Aware Entanglement Routing for Quantum Data Centers

## Outline

1. **Circuit-aware task modeling**
   - Quantum circuit, remote gates

2. **Topology-aware path selection**
   - QDC topology: Clos -> short path; BCube -> multi-path

3. **Joint routing and scheduling**

4. **Entanglement distribution**

## Description

Quantum data centers execute distributed quantum circuits by mapping remote gates
onto entanglement paths across structured network topologies. However, unlike
traditional routing problems, entanglement distribution must follow circuit
dependencies while competing for shared network resources such as switches and
Bell-state measurements. This thesis focuses on circuit-aware entanglement routing
and scheduling in quantum data centers, jointly determining which remote gates to
execute and how to assign paths under topology constraints. The objective is to
minimize execution latency and improve the reliability of distributed quantum circuit
execution.

## Key words

Quantum Data Centers, entanglement routing, topology-aware routing

## Inspired by

Quantum Data Center Infrastructures: A Scalable Architectural Design Perspective
