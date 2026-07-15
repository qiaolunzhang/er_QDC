**Quantum Data Center Infrastructures: A Scalable Architectural Design Perspective** 

Hassan Shapourian, Eneet Kaur, Troy Sewell, Jiapeng Zhao, Michael Kilzer, Ramana Kompella, and Reza Nejabati _Cisco Quantum Labs, Santa Monica, CA 90404, USA_ 

This paper presents the design of scalable quantum networks that utilize optical switches to interconnect multiple quantum processors, facilitating large-scale quantum computing. By leveraging these novel architectures, we aim to address the limitations of current quantum processors and explore the potential of quantum data centers. We provide an in-depth analysis of these architectures through the development of simulation tools and performance metrics, offering a detailed comparison of their advantages and trade-offs. We hope this work serves as a foundation for the development of efficient and resilient quantum networks, designed to meet the evolving demands of future quantum computing applications. 

## **I. INTRODUCTION** 

Quantum computing promises to solve complex problems beyond the reach of classical systems, but realizing its full potential requires the ability to operate millions of qubits. Current quantum processing units (QPUs) are limited to only tens or hundreds of qubits, well below the scale necessary for achieving practical quantum advantage. To bridge this gap, the concept of a quantum data center has been proposed, where multiple QPUs are networked together, enabling a distributed architecture that can scale to meet the demands of large-scale quantum computing [1–3]. Ultimately, these quantum data centers will form the backbone of a global quantum network, or quantum internet, facilitating seamless interconnectivity on a planetary scale [4, 5]. 

Quantum data centers (QDCs) [6] present a compelling solution to the limitations of individual quantum processors, leveraging interconnected QPUs to form a distributed quantum computing infrastructure. This model offers not only the scalability needed for large-scale quantum computation but also the economic and operational benefits of centralized quantum resources in a controlled environment. However, the architecture of such a quantum data center must address a variety of challenges, including qubit transfer with a reasonable rate and fidelity, network latency, and the probabilistic nature of quantum entanglement generation and distribution [7]. 

In this work, we propose scalable architectures for quantum data center networks, inspired by principles of classical data center networking. Our design leverages a dynamic, circuit-switched quantum network to facilitate efficient entanglement distribution between QPUs using shared resources, such as Bell-state measurement devices, quantum memories, and entanglement sources. This approach enables on-demand, all-to-all connectivity across the quantum network while minimizing reliance on expensive quantum hardware, thus optimizing cost and scalability. 

Our proposed architectures stand in contrast to oneto-one (peer-to-peer) quantum network designs [2, 8, 9], where QPUs are sparsely connected via optical links, typically forming a nearest-neighbor topology. As depicted in Fig. 3, we propose connecting QPUs through 

a non-blocking photonic interconnect composed of optical switches and quantum devices, building on scalable concepts akin to Refs. [10–12] and expanded upon in Ref. [3]. We explore two categories of quantum network topologies based on classical data center networking paradigms: switch-centric and server-centric. In switchcentric topologies, the network provides direct optical links between every pair of QPUs, achieving full connectivity. Conversely, server-centric topologies offer a modular design with many optical links but without full allto-all connectivity, positioning them between traditional one-to-one architectures and switch-centric designs. 

While one-to-one topologies may suffice for smaller systems—where not every pair of QPUs requires direct physical connections—they become less practical as system size scales to tens or hundreds of QPUs distributed across multiple nodes. For such larger networks, more structured architectures are necessary to maintain high end-to-end fidelity and efficient entanglement generation rates. The modular hierarchy of our proposed architectures enhances scalability and interoperability by accommodating diverse device features and transducers. Additionally, by leveraging dedicated hardware for entanglement distribution, our approach reduces system overhead and unlocks further performance improvements. 

We propose several QDC network topologies inspired by classical data center architectures, including Clos, Fattree [13], HyperX [14], Bcube [15], and Dcell [16], serving as representative examples of switch-centric and servercentric designs. To support entanglement generation, we explore three distinct protocols, enabling QPUs to communicate using communication qubits equipped with spin-photon interfaces [17]. These interfaces can operate in different modes—emitter, scatterer, or a combination of both—depending on the protocol’s requirements. 

To enable efficient execution of distributed quantum computing jobs, we introduce the concept of a _network-aware_ quantum orchestrator, a framework designed to bridge physical-layer architectures with higherlevel quantum applications in QDC networks. The orchestrator takes circuit-level descriptions of quantum jobs and network topology as inputs and generates precompiled instructions for optical switches and quantum hardware components, which are executed by a classical 

2 

**==> picture [185 x 150] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a) Laser Laser<br>BSM<br>QPU 1 QPU 2<br>(b) Laser PD<br>QPU 1 QPU 2<br>(c) PD PD<br>BSM<br>QPU 1 ES ES QPU 2<br>**----- End of picture text -----**<br>


FIG. 1. Ebit generation protocols. (a) Emitter-emitter, (b) emitter-scatterer, and (c) scatterer-scatterer protocols. Without any frequency conversion, the (a) and (b) protocols are designed for intra-rack communication, while (c) can be adapted for inter-rack communications. In the latter case, non-degenerate entanglement sources can be used to generate two photons one at telecom and one at frequency ranges compatible with QPUs. 

central controller. 

Additionally, we include a simulation and benchmarking section focusing on circuit execution capabilities [18], where we evaluate the performance of our proposed architectures using a Clos topology for random quantum circuits [19–21] as well as algorithmic benchmarks [22]. By integrating physical-layer modeling, network protocols, and the network-aware quantum orchestrator, we analyze average network latency and quantum fidelity as key metrics, providing insights into the practical feasibility of our approach. 

The rest of our paper is organized as follows: Section II outlines the physical layer modeling approach and details the entanglement generation protocols. In Sec. III, we introduce the proposed QDC network architectures, followed by the presentation of the network-aware quantum orchestrator in Sec. IV. Section V focuses on numerical simulations and performance benchmarks to evaluate the proposed designs. Finally, Section VI concludes the paper with closing remarks and potential future research directions. Additionally, four appendices are included to provide extended discussions on QDC architectures, further details on physical layer modeling and simulations, and integer linear programming (ILP) formulations for specific steps of the quantum orchestrator. 

The generated entangled pairs are then consumed to execute remote gates between the data qubits of different QPUs. The inter-QPU entanglement pairs can be generated in various ways. We summarize the three most popular methods in Fig. 1, which we explain in detail later in Sec. II B. A common theme in these methods is that quantum communication between QPUs is performed by transmitting or receiving photonic qubits in the form of single photon states (in some enconding). The emission process or the scattering process is carried out such that it results in an entangling gate between the stationary (communication) qubit and the flying qubit. This requires an efficient spin-photon interface (see for example the recent review [17] on various technologies and simulation tools). In this section, we start by briefly reviewing the emission and scattering processes and finish by discussing the entanglement generation protocols. 

In this paper, we explore on-demand scheduling protocols [23, 24] where ebits are generated dynamically as needed and consumed immediately. This approach allows communication qubits to have lower quality (e.g., shorter coherence times) compared to data qubits, as they only facilitate the generation and immediate consumption of end-to-end entanglement without the need to store quantum information. However, this characteristic does not always hold true. For example, in continuous ebit protocols [25, 26], where a buffer of EPR pairs is maintained and ebits are consumed based on program requirements, high-quality communication qubits (or reliable quantum memories) are essential to preserve the fidelity of the endto-end ebits over time. 

Before getting into details of how entanglement is generated between flying photonic qubits and communication qubits, let us briefly review different encodings and present our notation. We denote the vacuum state by _|_ vac _⟩_ and the photonic mode creation and annihilation operators by _a_ and _a[†]_ , respectively. 

- Fock-space: This is also called presence/absence encoding. We identify the two states of the photonic qubit as 

**==> picture [197 x 14] intentionally omitted <==**

- Polarization: The computational basis for this encoding is defined as 

**==> picture [203 x 15] intentionally omitted <==**

where the subscript _h_ ( _v_ ) refers to a horizontally (vertically) polarized photon, respectively. 

## **II. MODELING THE PHYSICAL LAYER** 

We envision each QPU is equipped with two types of qubits: data qubits, used to carry out quantum computation, and communication qubits, used to generate and store entangled qubits (ebits) between different QPUs. The goal of QDC network is to enable entanglement generation between communication qubits of various QPUs. 

- Time-bin: The computational basis for a time-bin photonic qubit is defined as 

**==> picture [203 x 15] intentionally omitted <==**

where the subscript of the photon creation operator _e_ ( _l_ ) denotes the early (late) generation time, respectively. 

3 

**==> picture [233 x 135] intentionally omitted <==**

**----- Start of picture text -----**<br>
|f i<br>!o<br>| 1 i !r | 0 i<br>QPU<br>Q = QPU<br>**----- End of picture text -----**<br>


FIG. 2. An abstraction for the quantum communication ports of a QPU based on the interface between the communication qubit and photonic qubit. The optical circulator is used to separate the incoming (red) photonic qubit or coherent pulse from the (blue) outgoing photonic qubit. The energy level structure of communication qubit is shown above. 

We note that the polarization and time-bin encodings can be converted into each other by using linear-optic components such as polarizing beam splitter and fiber delay lines. As we explain below, ebit generation process ends with measuring photonic qubits using single-photon detectors, which is in turn used as a heralding signal for a successful attempt. However, different measurement modules are required for different encodings, and sometimes it is not possible to measure qubits in an arbitrary basis. For instance, the Fock space encoding only allows for measurement in the computational basis ( _|_ 0 _⟩_ , _|_ 1 _⟩_ ) due to superselection rules (i.e., there cannot be a basis to measure a qubit in a superposition of one photon and zero photon). 

## _1. Communication qubit as a quantum emitter_ 

The high-level idea here is that by manipulating the initial state of the communication qubit we can entangle the outgoing photon to the emitter via the emission process. The protocol here follows one step of the celebrated Linder-Rudolph protocol [27] and is a common approach in trapped-ion qubits [10] and superconducting quits [28]. 

In general, we initialize the communication qubit in a superposition state _|α⟩c_ = _[√] α |_ 1 _⟩c_ + _[√]_ 1 _− α |_ 0 _⟩c_ by sending a resonant pulse between _|_ 0 _⟩↔|_ 1 _⟩_ at _ωr_ where the pulse duration determines the superposition coefficient. Then, we send a resonant _π_ -pulse of _ωo_ which after possible spontaneous emission gives the following state 

**==> picture [211 x 13] intentionally omitted <==**

Given the Fock space computational basis in Eq. (1) for the photonic qubit, Eq. (4) describes an entangled state of photonic and communication qubits. 

Similarly, to create an entangled state with a time-bin flying qubit, we initialize the emitter state in a Hadamard state _|_ + _⟩c_ (corresponding to _α_ = 1 _/_ 2) by sending a resonant _π/_ 2-pulse at _ωr_ . Then, we send a resonant _π_ -pulse of _ωo_ which after emission yields the state 

**==> picture [196 x 24] intentionally omitted <==**

Note that the photon emitted at this instance corresponds to the early time bin. Next, we apply a _π_ -pulse of _ωr_ followed by another _π_ -pulse of _ωo_ where the state after the emission is found to be 

**==> picture [201 x 50] intentionally omitted <==**

## **A. Communication qubit-photon interface** 

We assume the communication qubit is characterized by Λ-type energy levels and only the transition _|_ 1 _⟩↔|f ⟩_ is active as shown in Fig. 2. Majority of our discussion and protocols can be easily adapted to other types of the energy levels such as the II-type (where there are two allowed optical transitions one for each logical state to transition to). Throughout this paper, we may use spin or stationary qubit to refer to the communication qubits and use photon or flying qubit to refer to the photonic qubit. We run the communication qubit in two modes: as a scattering center for incoming photons, and as a quantum emitter. 

In what follows, we use the subscripts _c_ and _p_ to refer to the communication qubit and the photonic qubit, respectively. 

which is a Bell pair between the emitter and the photonic qubit. After another _π_ -pulse of _ωr_ we can convert it to another form 

**==> picture [186 x 23] intentionally omitted <==**

if desired. It is worth noting that a spin-photon entangled state with a polarization encoding can be generated using a communication qubit with II-type energy levels where each transition is coupled to a particular polarization. In this case, the resonant _π_ -pulse is prepared in a superposition of the two polarizations [29]. 

To sum up, we initialize the state of communication qubits and arrange signals to make the emission process effectively a cnot _c,p_ gate where the control qubit is the emitter [30]. 

4 

## _2. Communication qubit as a scattering center_ 

As we see in Fig. 1, the (b) and (c) methods involve receiving a photonic qubit which after going through the QPU (which we call scattering process) is detected at photon detector (PD) modules. The scattering process is engineered to let the incoming photon and the communication qubit interact and effectively realize an entangling gate (aka, spin-photon gate). At the same time, the detection event need to perform a measurement in a superposition basis, e.g., Hadamard basis, to ensure transferring the entanglement to the scatterer. Because of that, the entanglement generation protocols based on scattering events are not applicable to the Fock-space encoding, where photonic qubits can only be measured in the computational basis. In what follows, we briefly discuss such effective gates. 

The first approach implies a deterministic controlledphase (cz) gate [29, 31] and works as follows: If the communication qubit is at _|_ 1 _⟩_ , an incoming photon at frequency _ωo_ is absorbed and reemitted back. The reemission process involves a full rotation in the twodimensional subspace ( _|_ 1 _⟩_ - _|f ⟩_ ) and gives a _π_ Berry phase. Because of this phase shift, a scattering event can be described by the following map 

**==> picture [198 x 58] intentionally omitted <==**

which is nothing but a cz gate considering the encoding defined in Eq. (1). Such spin-photon gates are demonstrated in atoms trapped in Fabry-Perot cavities [32], and quantum dots in photonic crystal waveguides [33, 34]. Similar to the emission process, this method can be readily adapted to time-bin encoding. Suppose we want to create a Bell state of the photonic and communication qubits. The incoming photonic qubit and the communication qubit are both initialized in the superposition state _|_ + _⟩c ⊗|_ + _⟩p_ = 2[1][(] _[|]_[0] _[⟩] c_[+] _[|]_[1] _[⟩]_[)] _[⊗]_[(] _[a] e[†]_[+] _[a][†] l_[)] _[ |]_[vac] _[⟩]_[.][Since photon] scattering always give a _π_ -phase shift, a simple way of implementing the controlled-phase gate is by only letting the early time-bin interact with the communication qubit via an 1-to-2 optical switch (e.g., a phase-tunable MachZehnder interferometer) and rerouting the late time-bin. This leads to the following Bell state 

process is based on the fact that a photon can only be reflected if the communication qubit is in _|_ 1 _⟩_ state (c.f. Fig. 2), and hence a successful gate is heralded by detection of a reflected photon. This approach is experimentally realized in SiV centers in diamond photonic crystal cavities [35–37] and entangling two neutral atoms in a cavity [38]. To illustrate how this approach works, we again initialize the system with the product state _|_ + _⟩c ⊗|_ + _⟩p_ = 2[1][(] _[|]_[0] _[⟩] c_[+] _[ |]_[1] _[⟩] c_[)] _[ ⊗]_[(] _[a] e[†]_[+] _[ a][†] l_[)] _[ |]_[vac] _[⟩]_[.][Right][after] the early time-bin passes, we apply a _π_ -pulse of _ωr_ to flip _|_ 0 _⟩c_ and _|_ 1 _⟩_ . A detection event then projects the state into an entangled state ~~_√_~~ 12[(] _[|]_[0] _[⟩][c][⊗][a] e[†][|]_[vac] _[⟩]_[+] _[|]_[1] _[⟩] c[⊗][a][†] l[|]_[vac] _[⟩]_[)][.] This is because only state _|_ 1 _⟩c_ can reflect the photon. Compared to the deterministic spin-photon gates, Bell carving is simpler to realize as it does not require strong coupling. However, this process is inherently probabilistic as it involve post-selection. In other words, the maximum success probability of the Bell carving is 50% even in the absence of other causes for the photon loss. 

## **B. Entanglement generation protocols** 

In this part, we explain the three main entanglement generation protocols as outlined in Fig. 1. We shall refer to these protocols using the operating modes of the two communication qubits in the two end-QPUs as follows: Emitter-emitter, emitter-scatterer, and scattererscatterer. We further discuss the performance of each protocol in terms of the end-to-end entanglement generation rate and fidelity following the earlier work [10, 39, 40] across different platforms. 

In short, the emitter-emitter protocol involves both communication qubits running as emitters and the photons being directed to a Bell-state swapping module (BSM) to perform entanglement swapping (and a heralding signal). In the emitter-scatterer protocol, one communication qubit runs as an emitter and the other as a scatterer, where the heralding signal is generated from a photon detector connected to the second QPU. In the scatterer-scatterer protocol, both communication qubits run as scatterers and non-degenerate entanglement sources and BSMs are utilized to distribute entanglement. We further discuss which hardware platforms are more suitable for which protocols. We recall that the latter two protocols are not applicable to the Fock-space enconding of photonic qubits as discussed in Sec. II A 2. 

**==> picture [189 x 24] intentionally omitted <==**

A drawback of the scattering process is that approach requires a strong coupling of photons with the communication qubit. Although strong coupling regime can be realized by confining the light with photonic cavities or waveguides, this technology may not be available in all platforms. 

Another approach is based on the conditional photon reflection, which is also referred to as “carving”. This 

## _1. Emitter-emitter protocol_ 

This protocol is shown in Fig. 1(a), where we drive both communication qubits in the two end QPUs to emit photons and then post-select the two-qubit measurement outcome of the BSM in the middle. The BSM is often realized by linear optics and single photon detectors, and as such their success probability is 50% regardless 

5 

of the qubit encoding. Boosted BSM with linear optics can surpass the 50% limit but requires additional ancillary photons [41–43]. Considering the Fock-state encoding of photonic qubits, where the initial communication qubit-photon entangled state is given by Eq. (4), the BSM can be implemented by a beam splitter with two single-photon detectors at the two output ports. A single photon detection in either detectors heralds the creation of the state 

**==> picture [221 x 24] intentionally omitted <==**

with the success probability of 2 _α_ (1 _−α_ ), where we group together the communication qubit states, _|qc_ 1 _qc[′]_ 2 _[⟩]_[=] _|q⟩c_ 1 _⊗|q[′] ⟩c_ 2, and _k_ ∆ _x_ arises due to differences in optical path lengths [10]. We note that the success probability is further reduced due to photon loss during transmission from each QPU to the BSM. In particular photon loss may cause a false positive signal. As a result, a single photon detection event yields a noisy Bell state in ˆ the form of _ρ±_ = (1 _− w_ ) _|ϕ±⟩⟨ϕ_ + _|_ + _w |_ 11 _⟩⟨_ 11 _|_ , and the resulting fidelity is then given by _F_ ee[(F)] = 1 _− w_ , where 

**==> picture [154 x 24] intentionally omitted <==**

and the overall success probability is found to be 

**==> picture [167 x 13] intentionally omitted <==**

with _α_ the initial state parameter defined in Eq. (4) and _η_ = _η_ eb _η_ det the overall end-to-end photon transmission rate (i.e., overall photon loss rate is 1 _− η_ ) including the detection efficiency of single-photon detectors _η_ det and the transmission probability from the emitter to the BSM _η_ eb. As we see from the above expressions, in the lossy channel regime _η ≪_ 1 the larger _α_ leads to higher success probability at the cost of lower fidelity. Therefore, depending on the application and system characteristics we may choose values different from _α_ = 1 _/_ 2 in Eq. (4). In the above analysis, we neglected optical path difference which is usually a good assumption provided that the optical path difference between two emitters are at the wavelength level of photonic qubits; otherwise, the mismatch leads to a phase factor and the imbalance in transmission rate along the two paths _ηe_ 1 _b_ = _ηe_ 2 _b_ results in the entanglement between the two emitters being a noisy Bell state, as they are not maximally entangled. 

Because of the probabilistic nature of the EPR pair generation, we consider a repeat-until-success protocol, where we keep trying to generate an EPR pair until we get the positive signal in the BSM. Mathematically, the number of trials is a random variable _N_ described by the geometric distribution _P_ ( _N_ = _n_ ) = _p_ ee[(F)][(1] _[−][p]_[(F)] ee[)] _[n][−]_[1] and the duration time is _Nτ_ 0, where _τ_ 0 is the operation time for each attempt. Hence, the average time for a successful EPR pair generation is _Nτ_ 0 = _τ_ 0 _/p_ ee[(F)][,][which] implies the average generation rate 

**==> picture [194 x 23] intentionally omitted <==**

We provide some back of envelope estimate of the resulting rate and fidelity in the next section. 

It is important to note that the emitted photons in the above protocol run at the qubit resonant frequency which are typically in the visible or near-infrared (NIR) frequency range (700-900nm) assuming atomic based or trapped ion quantum computing platforms. Therefore, this protocol by construction (unless we perform quantum frequency conversion to telecom range) is only suitable for short-range quantum communication such as the same-rack entanglement pair generation. We comment more on this issue in the next section as we present the network architectures. 

As mentioned, the emitter-emitter protocol based on the Fock-space encoding is sensitive to optical path difference. These challenges can be mitigated by adapting the protocol to time-bin encoding. In this case, the initial spin-photon entangled state is given by Eq. (7) and the BSM must split the time bins to path encoding before sending them to two beam splitters (associated with early and late time bins) each with two single-photon detectors at their output ports. Unlike the Fock-space encoding, a coincidence event in two detectors each of which attached to a different beam splitter heralds the creation of the state in the same form as Eq. (10), not a mixed state. In other words, there is no false positive event with time-bin (or polarization) encoding if we neglect the detector’s dark count, and the nominal fidelity of the heralded states can reach unity even in the presence of photon loss. As mentioned, a successful event requires arrival of two photons (each with probability _η_ eb _η_ det) and generating a time-bin spin-photon entangled state takes _τ_ 0 + _τ_ b where _τ_ b denotes the time difference between the two time bins. Similar to the Fock-space encoding the randomness of the generation process is described by a geometric distribution with the success probability _p_ ee[(T)] = _η_ eb[2] _[η]_ det[2][.][Therefore,][the][entanglement][generation] rate on average is given by 

**==> picture [164 x 25] intentionally omitted <==**

where the factor of 2 in the denominator is due to the post-selection of the measurement outcomes in the BSM. 

**==> picture [121 x 9] intentionally omitted <==**

This protocol is shown in Fig. 1(b), where the first (emitter) communication qubit is coherently driven to emit a photon which is then received by the other (scatterer) communication qubit and ultimately measured in the photon detector. As mentioned, this protocol is not applicable to Fock-space encoding of photonic qubits, so we consider the time-bin encoding for example, where the initial emitter-photon state is given by Eq. (7). A successful heralding event at the scatterer thus leads to a Bell-pair of the two communication qubits as in Eq. (10). 

6 

A successful event here requires the detection of the emitted photon which implies _p_ es[(T)] = _η_ eb _η_ det ( _η_ es denotes the transmission probability from the emitter to the scatterer) and takes spin initialization and state preparation of _τ_ 0 + _τ_ b. Hence, the average end-to-end entanglement generation rate is found to be 

**==> picture [164 x 21] intentionally omitted <==**

where the factor of 2 in the denominator is due to the post-selection of the measurement outcomes using the Bell carving scheme (c.f. II A 2). We note that the nominal fidelity of the heralded states in this protocol can reach unity since there is no false positive event if we neglect the detector’s dark count. Since only a single photonic qubit is transmitted through the network, this protocol imposes fewer requirements for qubit stabilization and synchronization compared to the emitteremitter protocol. Consequently, the emitter-scatterer protocol is more advantageous in scenarios where stabilizing and synchronizing multiple photonic qubits pose significant challenges. 

## _3. Scatterer-scatterer protocol_ 

As shown in Fig. 1(c) this protocol starts with two entanglement sources generating two entangled pairs of photons and direct one photon to the BSM in the middle and send the other photon to the end-QPUs. A successful attempt of generating an end-to-end entanglement is heralded by the simultaneous occurrence of three detection events: Two scattering detection events and one coincidence event at the BSM. The use of entanglement sources in this protocol offers both advantages and challenges. One notable benefit is the utility of nondegenerate sources, which generate pairs of entangled photons at distinct frequency ranges—for instance, nearinfrared (aligned with the communication qubit’s resonant frequency) and telecom (compatible with optical fibers and standard off-the-shelf devices). This pairing facilitates interfacing between two remote QPUs without relying on underdeveloped quantum frequency converters or transducers. 

However, the most commonly available entanglement sources, such as those based on spontaneous parametric down-conversion (SPDC) or spontaneous four-wave mixing (SFWM), have an inherently probabilistic generation process. The stochastic nature of photon pair generation, combined with the requirement for three successful detection events, results in significantly low end-to-end ebit generation rates. While synchronization challenges can be mitigated using quantum memories at the BSM stage, our analysis below demonstrates that the advantages of this protocol—even without quantum memories—justify its adoption in the near term. 

We consider the entanglement sources generate a time- 

bin entangled state of photons 

**==> picture [228 x 23] intentionally omitted <==**

where _a[†]_ and _b[†]_ denote the creation operator of the two entangled photons (aka signal and idler photons), and the subscripts contain two parts: the first index _i_ = 1 _,_ 2 refers to the output of the first and second entanglement sources, respectively, and _ti_ is the _i_ -th source photon wavepacket’s (mean) characteristic time (c.f. Eq. (A1) in Appendix A). Similar to before, _τ_ b denotes the time difference between the two time bins. A possible way to generate time-bin entangled pair of photons is by splitting an input pulse into two pulses (or bins) by sending it through an interferometer before entering the nonlinear medium [44]. The fact that the generation time is stochastic implies that _ti_ is a random variable. Without making any assumption about details of the entanglement sources, we consider the pair generation to be governed by a Poisson distribution with an average rate _λ_ , which physically corresponds to the effective end-to-end (source-to-detector) rate. 

Without the use of quantum memories, we propose a brute-force protocol by which we continuously pump the entanglement sources and look for coincident events across the aforementioned three end points. If we observe a detection event at any of the QPUs but not all three locations, then we reinitialize that communication qubit and reject any events during the reinitialization. The underlying reason that this approach gives a finite end-toend ebit generation rate is that the photon wavepackets have some linewidth ∆ _ω_ in frequency domain (or broadening in time) which leads to some finite probability for the coincidence as long as _|t_ 1 _− t_ 2 _|_ ≲ ∆ _ω[−]_[1] . To capture this effect accurately, we numerically simulate this protocol and study the statistics of the time takes to observe a successful event (see Appendix A for details). We find that the end-to-end generation time _T_ ss follows an exponential distribution 

**==> picture [174 x 12] intentionally omitted <==**

where the average ebit generation rate is nothing but the exponential distribution parameter _Rss_ = _T_ 1ss[=] _[ λ]_[ss][.][We] observe that the parameter _λ_ ss = _f_ ( _τ_ 0 _,_ ∆ _ω_ ) generally varies as we change the photon linewidth and the qubit initialization time. Check out Appendix A for plots showing these functional dependencies. 

In principle, the nominal fidelity of the heralded states in this protocol can also reach unity since there is no false positive event provided that we neglect the detector’s dark count. 

## **III. NETWORK ARCHITECTURE DESIGNS** 

We envision a network of interconnected QPUs to not only increase the scalability of computing but also facilitate the maintenance of the stringent physical conditions 

7 

**==> picture [506 x 140] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a) Clos  (b) BCube<br>BCube1<br>Rack1 Rack2 BCube0<br>QPU1 QPU2 QPU3 QPU4<br>QPU1 QPU2 QPU3 QPU4<br>**----- End of picture text -----**<br>


FIG. 3. Quantum data center network architectures: (a) Clos topology, (b) BCube topology, as a representative architecture for switch-centric and server-centric topologies, respectively. We use two types of switches: Telecom switches (dark blue diskshaped) and near-infrared switches (blue rectangular cubes). Lines connecting switches are optical fiber bundles. 

QPUs demand. We base our design on a set of guiding principles to achieve a modular, scalable, and nonblocking quantum interconnect. As we explain further in this section, our architecture utilizes an optical network fabric to distribute entanglement among QPUs. 

First, we look for modular designs with an effective on-deamnd all-to-all connectivity while saving on number of expensive quantum hardware. As a result, our architecture involves a dynamic circuit-switched network where the ebits are generated across the quantum network by a limited set of shared resources such as BSMs, entanglement sources, quantum memories, etc. Second, for quantum network topology design, we draw inspiration from classical data center networks [45] based on switch-centric and server-centric configurations. Third, we make informed decisions on the type of ebit generation protocol suitable for various topologies and over different length scales. As we discuss in the next section, we consider a classical control plane in charge of reconfiguring the optical switches and reserving the necessary quantum network devices to create an end-to-end optical paths between the communication qubits and run multiple attempts to generate ebits. 

In what follows, we dive deep into two types of architectures for DQCs as shown in Fig. 3. In classical data center networks, switch-centric topologies depend on switches for interconnection and routing, whereas server-centric topologies utilize servers equipped with specialized network interface cards (NICs) to facilitate interconnection and routing. A general observation is that the former mainly scale up in a vertical manner, i.e., increasing the number of switch ports or increasing port speed directly, which leads to a high cost for a large-scale data center. In contrast, the latter offer a more flexible network innovation and customization due to the openness and programmability of server hardware and software. We believe that this difference applies to the quantum version of these architectures as well. However, a new challenge which is intrinsically quantum arises in server-centric quantum networks: The interconnection and routing in- 

volve a repeater chain for a subset of QPU pairs, where some QPUs play the role of quantum repeaters and require to perform entanglement swapping to generate an end-to-end ebit. We expand more on this below. 

## **A. Switch-centric networks** 

Figure 3(a) shows a Clos network as an example of switch-centric topologies. The QPUs are grouped together in several racks which are internally connected via top-of-rack (ToR) switches. The racks are in turn connected via a hierarchically connected set of optical switches. The switches are equipped with various quantum hardware devices to enable the ebit generation protocols. To address the frequency mismatch between the qubit resonant frequencies and telecom wavelengths, we consider short-distance (intra-rack) communications to operate at native qubit frequency (usually at 700-900nm, i.e., near infrared regimes for atomic or ionic platforms) while long-distance (inter-rack) communications to operate at the telecom wavelengths. In other words, the upper part of the network above the ToR switches (as shown in Fig. 3(a)) operates at the telecom range while the lower part within each rack operates at the NIR regime. 

We consider emitter-emitter or emitter-scatterer protocols for the intra-rack ebit generation and scattererscatterer for the inter-rack ebit generation. As a result, the ToR switch and all components attached to it run at NIR frequency range, except the entanglement sources the output of which going to the ToR switch runs at NIR and the other output runs at telecom. Therefore, we must use non-degenerate entanglement sources for this purpose. Alternatively, the conversion from NIR to telecom at the ToR switch ports can be done via quantum frequency converters(QFCs) [37, 46–49]. To extend the communication range to other racks, we consider converting the NIR photon into telecom regime and back via QFCs. 

The rationale behind this choice of hybrid operation is 

8 

that we prefer to maintain a small overhead for moderate quantum jobs, which can be done by a small number of QPUs, since the protocols involving QFCs or nondegenerate entanglement sources may be slow and/or have low fidelity although these technologies are under rapid development. We briefly discuss the quantum adaptation of other popular switch-centric topologies such as Fat-tree and HyperX in Appendix B 1 and summarize the number of network components in Table III. 

## **B. Server-centric networks** 

As Fig. 3(b) shows, a server-centric topology is characterized by smaller switches with fewer ports but QPUs with multiple ports. Here, we illustrate a novel architecture inspired by the BCube topology [15]. We note that server-centric topologies entirely operate at the NIR frequency range, and the ebit generation protocol of choice is the emitter-emitter method although the emitter-scatterer method may be necessary (e.g., for DCell topology). As mentioned earlier, the major challenge with such topologies is that they do not provide direct optical paths between every pair of QPUs, e.g., QPU _i_ and QPU _j_ of two different BCube containers. For instance, in order to establish entanglement between QPU1 of BCube0 and QPU2 of BCube1, we first need to generate two elementary link entanglements: one between QPU1 of BCube0 and QPU1 of BCube1, and the other between QPU1 and QPU2 of BCube1. This is nothing but the first generation repeater networks [50], where intermediate QPUs play the role of quantum repeaters. In other words, routing and resource management in server-centric topologies involve dealing with repeater networks which is a vast topic by itself (see for example a recent survey [51] and references therein). That said, compared to long-distance quantum communication and repeater networks in general, QDC-scale network enjoys an efficient global control plane and does not deal with an arbitrary network graph. Furthermore, the entanglement swapping can be made deterministic because QPUs are in principle capable of applying deterministic gates between their communication qubits. In fact, further simplification may arise due to the existence of many parallel shortest paths (repeater chains) between two QPUs. However, a full network-aware quantum orchestrator in such network topologies is still fairly complex and out of scope of the current work. We shall focus on switch-centric topologies when discussing the quantum orchestrator and presenting numerical simulations 

We now briefly explain the modularity and scalability of server-centeric topologies using the BCube topology as an example. This topology is deliberately designed for modularly scalable data centers and can be expanded hierarchically to interconnect a large number of QPUs. For every expansion, the number of switches required at the added layer is jointly determined by the number of 

ports on switches and the number of layers in the network, e.g., there is one layer _k_ = 1 in Fig. 3(b), and each switch has four ports _n_ = 4. BCube0 is obtained by connecting _n_ QPUs to an _n_ -port switch. When building BCube1, an additional _n_ upper-layer switches are required. Each upper-layer switch is connected to all _n_ BCube0 containers, thereby constructing a larger BCube network recursively. The number of QPUs that a _k_ -layer BCube can hold is _n[k]_[+1] , at the cost of _k_ + 1 ports at each QPU. There is a unique path between QPUs with the same index across the network, and there are at most _k_ + 1 parallel paths (repeater chains) between any pair of QPUs in BCubek. 

We present some additional server-centric topologies in Appendix B 2 and summarize the number of network components in Table III. 

## **IV. NETWORK-AWARE ORCHESTRATOR FOR DISTRIBUTED QUANTUM COMPUTING** 

Our focus in this paper is to lay foundations for the novel (physical layer) architectures for quantum data center networks. However, to have a working platform to perform distributed quantum computing jobs (in the form of quantum circuits of logical qubits), we see a need for several intermediate layers from ebit generation protocols on the physical layer all the way up to executing quantum applications. Along this line, the first step is to provide a framework for controlling the quantum hardware and switches to execute quantum jobs in a distributed manner. In this section, we present the basic building blocks of such a framework which we call the quantum orchestrator. As shown in Fig. 4, this framework takes circuit-level description of quantum jobs as well as quantum network topology (including quantum hardware distribution across the network) as inputs and returns a set of instructions for optical switches (and other quantum hardware components). We note that these instructions are generated (offline) in advance, and are eventually executed by a classical central controller [52–54] to establish end-to-end ebits and consume them to execute remote gates. 

We split the job of the quantum orchestrator into two steps: First, a circuit compilation where the circuit may be modified to be compatible with physical layer constraints, and ultimately logical qubits in the quantum circuit are mapped into physical qubits inside QPUs. Second, a network scheduling which goes through a given quantum circuit and finds a minimal sequence of commands for optical switching to perform remote gate execution based on the qubit mapping and available network resources. 

In what follows, we present a working version of the quantum orchestrator. The overall objective is to minimize the computation time and infidelity. It is worth noting that remote gates are generally slower and noisier compared to the local gates (see Sec. V for some realistic 

9 

**==> picture [183 x 103] intentionally omitted <==**

**----- Start of picture text -----**<br>
Quantum circuit<br>Circuit compiler<br>QDC network<br>topology<br>Network scheduler<br>Control commands<br>**----- End of picture text -----**<br>


FIG. 4. Pipeline for the proposed network-aware distributed quantum computing orchestrator. 

numbers); hence, our objective is equivalent to reducing the number of remote gates, and among the remote gates selecting the less noisy ones (e.g., choosing the intra-rack communications over the inter-rack ones in switch-centric architectures). As we explain, each step of the quantum orchestrator may be broken down to several optimization sub-problems which require a more detailed analysis. We postpone the discussion on such details to future work. 

## **A. Circuit compiler** 

The primary function of this module is to take an input quantum circuit of logical qubits and map these logical qubits to physical qubits within QPUs. In general, finding an optimal qubit mapping is an NP-hard problem [55], and there is extensive literature on advanced algorithms for this purpose, including improvements over traditional graph partitioning methods like the KL and METIS algorithms [56, 57]. In this paper, we consider a basic compiler with a static circuit partitioning algorithm; i.e., logical qubits are assigned at the beginning and inter-QPU gates are executed via gate teleportation. We rely on heuristics to determine a qubit mapping that minimizes the number of remote gates, using standard graph partitioning techniques [56, 57]. For simplicity, we assume that the input quantum circuit consists of only single-qubit and two-qubit gates; if not, it is transpiled into this form. While this assumption facilitates the use of graph partitioning algorithms, other circuit partitioning methods [55] exist that do not require it. We also assume that qubits inside the QPUs have all-to-all connectivity (as in trapped-ion or atomic based processors), otherwise, the compiler needs to modify the circuit to be compatible with the qubit connectivity patterns. Again, this is a standard step in circuit compilation and the existing tools can be adopted for this purpose. Besides that, quantum circuits can be designed based on the algorithm and the hardware constraints. This process is generally known as quantum architecture search (QAS) [58]. Our choice of compiler is simple but sub-optimal, and there are various ways for improvement such as allowing for qubit teleportation. This leads to adaptive circuit partitioning schemes [59, 60] which will be detailed in a sep- 

arate work [61]. 

For hybrid architectures that employ different protocols for generating ebits between QPUs located on the same rack and those on different racks, we address an additional optimization problem of assigning QPUs to racks. Specifically, we minimize an objective function, defined as a weighted sum of inter- and intra-rack ebits, with weights determined by the logarithms of their respective fidelities. As detailed in Appendix C, this optimization can be formulated as an integer linear program. Additionally, in Ref. [61], we extend the rack assignment problem to a more generalized setup involving an arbitrary number of link types. 

## **B. Network scheduler** 

This module provides a set of commands, known as a network schedule, that sequentially controls quantum hardware and optical switches, managed by a central controller. Remote two-qubit gates are executed using the gate teleportation protocol [62], which consumes two ebits per remote gate. A key feature of this protocol is that the control qubit remains in its original QPU, unlike qubit teleportation, which modifies the qubit layout by moving the control qubit to the QPU containing the target qubit. Given that ebit generation is generally much slower than local gate execution, we ignore the local gate execution time, assuming it is effectively instantaneous. Here, we consider on-demand framework for switch-centric networks, where we generate ebits precisely when they are required for a specific remote gate. Further generalization to server-centric networks involve repeater network protocols since some QPUs cannot be directly connected. We imagine implementing repeater protocols within the data center based on asynchronous parallel protocols with entanglement swap as soon as possible [63–66]. 

The scheduling commands encompass reconfiguring optical switches and allocating the necessary quantum network devices to establish an end-to-end optical path between the communication qubits. Multiple attempts are made to generate ebits until a heralding signal confirms success. Depending on the protocol, these commands require synchronization across devices, including the terminal QPUs, to ensure coordinated execution. 

We first describe the scheduling algorithm for a single job scenario, i.e., scheduling for a quantum circuit. To create an effective schedule, we need to address two key issues: tracking gate dependencies (as gates acting on shared qubits may not commute) and optimizing for minimal switching events (to reduce latency) while maximizing network utilization by executing independent gates in parallel wherever possible. 

Gate dependencies are managed by applying a topological sorting algorithm to the quantum circuit computation graph, represented as a directed acyclic graph (DAG) [67, 68]. We use a modified version of Kahn’s al- 

10 

**==> picture [470 x 175] intentionally omitted <==**

**----- Start of picture text -----**<br>
1 (i) (ii) (iii)<br>2<br>3<br>4<br>5<br>6<br>4 3 1 2 5 6 4 3 1 2 5 6 4 3 1 2 5 6 4 3 1 2 5 6<br>g(4,3) g(1,2) g(6,5) g(4,3) g(1,2) g(6,5) g(4,3) g(1,2) g(6,5) g(4,3) g(1,2) g(6,5)<br>g(1,4) g(2,5) 6 g(1,4) g(2,5) 6 g(1,4) g(2,5) 6 g(1,4) g(2,5) 6<br>g(3,1) 4 5 2 g(3,1) 4 5 2 g(3,1) 4 5 2 g(3,1) 4 5 2<br>1 3 1 3 1 3 1 3<br>**----- End of picture text -----**<br>


FIG. 5. An instance of applying our scheduling algorithm to a quantum circuit of 6 qubits on a network of 6 QPUs. The circuit and its equivalent DAG are shown on the left. The other panels illustrate the step-by-step schedule of remote gates starting from the DAG frontier nodes. At each step, a set of remote gates to be executed are highlighted (while the rest are grayed out) and the corresponding switch configurations are shown as end-to-end paths. See the text for more details. 

gorithm, designed to track dependencies while enhancing efficiency, as detailed below. The scheduling algorithm proceeds by iterating through three main steps until all gates in the DAG are scheduled. The set of commands are stored in the list _W_ total. 

**Step 1:** Identify the set of independent gates (also known as frontier nodes in the DAG) and add them to a set _I_ . These are gates with no unexecuted dependencies, meaning they have no incoming edges in the current DAG state. 

**Step 2:** Sort the independent gates in descending order based on the number of dependent gates (i.e., the number of successors in the DAG). Starting with the gate with the most dependencies, if the gate is remote, reconfigure the switches to establish an end-to-end path and allocate the required quantum devices along this path. For path selection, we always choose the shortest available path between two QPUs. Record the reconfiguration commands and allocated resources in _W_ . Remove the corresponding node from the DAG. If a path or required resources are unavailable, proceed to the next gate in the list. 

**Step 3:** Continue looping through Steps 1 and 2 as long as there are available optical paths and network resources. Once resources are exhausted, the list _W_ contains all commands for the current round of switching events. Add _W_ to _W_ total, clear _W_ , and return to Step 1. 

We note that in step 2 a heuristic approach is employed for resource management to mitigate routing and congestion. As detailed in Appendix D, the complete resource management problem maps to a multi-commodity multi-flow problem, which can be formulated as an integer linear program. However, we opt for this heuristic method, which offers faster and more scalable performance for larger quantum jobs. 

Figure 5 illustrates the above steps for a small quan- 

tum circuit on a network of two racks. Here, for clarity we show one qubit per QPU and assume there is one BSM per switch. The corresponding DAG is shown below the circuit. We use the same convention for DAG as Qiskit DAG [67], where qubits are shown as input and output vertices, gates are core vertices and edges connect input vertices to output vertices through the gates. Following the above steps, first it is evident from DAG that cnot gates acting on (1 _,_ 2), (4 _,_ 3), and (6 _,_ 5) are frontier nodes (here ( _c, t_ ) denote the control and target qubits of a cnot gate, respectively). We check that we have the resources to satisfy all these gates in parallel (step 2) and further see that we fully utilize the network resources (step 3). Hence, this forms our first switch configuration which is shown as (i) in the figure. Next, we go back to step 1 and look for a new set of independent gates and find that they are (1 _,_ 4) and (2 _,_ 5). However, we cannot execute both in parallel since there is only one BSM attached to the core (telecom) switch. Because gate (1 _,_ 4) has a successor in the DAG, we prioritize it and that becomes the next configuration (ii). Lastly, we are left with two independent gates (2 _,_ 5) and (3 _,_ 1) which can be executed in parallel. This forms the final switch configuration denoted as (iii). 

Next, we discuss how to extend this algorithm to handle multi-job scheduling. Jobs may arrive at random times, including during the scheduling or execution of other jobs. In this approach, we do not assume prior knowledge of incoming jobs; instead, we learn about them as they are received. A different variant of multi-job scheduling arises in multi-tenancy scenarios, where we have a full list of jobs to be executed in the quantum data center and aim to find an optimal joint schedule that minimizes both latency and infidelity. We plan to address this latter problem in future work. 

The first step in the multi-job scheduler is to maintain a job buffer, where we check if there are sufficient 

11 

resources (in terms of available compute qubits) to accommodate an incoming job. If resources are available, we compile the circuit based on the unassigned QPUs and move the job to a scheduling list, where its DAG is added to the existing DAG being scheduled. If sufficient resources are not available, the job is placed in a waiting queue. This queue regularly checks for available QPUs and uses a first-in-first-out (FIFO) approach to assign pending jobs to free QPUs. If the waiting queue reaches capacity, the job is rejected. 

In the multi-job setting, we extend Steps 1-3 from the above algorithm to operate across multiple DAGs, each associated with a different job. To ensure fairness, we introduce an additional condition in Step 2: we loop over all DAGs, scheduling one gate per DAG in each iteration. This approach balances the execution of tasks across multiple jobs.This approach can further be improved to account for efficiency by prioritizing smaller jobs (with shallower circuit depth, fewer qubits, or both) when scheduled with large jobs so that they get executed faster instead of slowed down because of concurrency with those large jobs. Beyond that, there are numerous other opportunities for further optimization throughout the compilation and scheduling stages, which we plan to explore in future work. 

## **V. PERFORMANCE ANALYSIS** 

In this section, we present some simulation results where we combine physical layer modeling, network protocols, and network-aware orchestrator. For the QDC architecture, we focus on the Clos topology with hybrid protocols for intra- and inter-rack quantum communications. Because of the probabilistic nature of entanglement generation protocols, we use average quantities to estimate average network latency, i.e., how long the circuit execution takes on average, and a proxy for circuit fidelity, i.e., how noisy the platform is. Although these two quantities, namely, rate and fidelity (or their variants), can be combined to define a quantum network utility function [69, 70]; we focus on addressing them separately in this paper. 

As mentioned in the previous section, a network schedule is a list of switching events. Each switching event consists of a set of ebits to be generated in parallel. Let _nr_ be the number of pairs of QPUs which need to generate ebits at _r_ -th round of switching and _ti_ denote the time it takes to generate an ebit for _i_ -th QPU pair with _i_ = 1 _,_ 2 _, · · · , nr_ . Hence, the duration of this switching event is given by 

**==> picture [179 x 12] intentionally omitted <==**

where _ti_ is a random number which is simply related to the number of attempts until success and whose probability distribution depends on the ebit generation protocol (c.f. Sec. II B). The overall execution time is then found 

by aggregating the duration of switching rounds 

**==> picture [169 x 22] intentionally omitted <==**

with an additional contribution due to the reconfiguration time _τ_ sw of optical switches in each round. In our numerical evaluations, we compute an estimate for the expectation value of each round duration Eq. (18) using Monte-Carlo, i.e., by sampling from the distribution of each _ti_ and aggregate the result over many iterations. 

We also calculate a weighted sum of number of gates as a proxy for the quality of distributed quantum computation. Concretely, for _M_ types of gates (including local and various non-local types) we define a cost function as follows 

**==> picture [177 x 30] intentionally omitted <==**

where _ni_ is the number of _i_ -th type gates and _Fi_ denotes the respective average fidelity of these gates. We choose one of the gate types as a baseline and work with the ratios of log fidelities which do not depend on log basis anymore. It is important to note that the quantity (20) is a measure of infidelity, i.e., the smaller the better (see Appendix C for derivation details). In our analysis we only consider two gate types intra- and inter-rack gates and this expression is simplified into 

**==> picture [246 x 37] intentionally omitted <==**

We now present the numerical values we plug in to our numerical analysis. We consider emitter-emitter protocol with Fock space encoding for intra-rack communications as explained in Sec. II B 1. Considering hardware parameters from Refs. [10, 47, 71, 72] _α_ = 0 _._ 05, _η_ = 0 _._ 1 (i.e., 10 dB loss), and _τ_ 0 _[−]_[1] _∼_ 1 MHz, we obtain _τ_ ee = 0 _._ 1 ms and _F_ ee = 0 _._ 95 for the same rack EPR pair generation. For the inter-rack communication, we use scatterer-scatterer protocol where the end-to-end ebit generation rate depends on various hardware parameters as discussed in Sec. II B 3. With some reasonable parameters such as 10[6] end-to-end photon pair generation of entanglement source with 1GHz photon linewidth, and 1 _µ_ sec qubit reset time, the exponential distribution parameter becomes _λ[−] ss_[1] = 10msec. We also consider the average optical switch reconfiguration time to be _τ_ sw = 1msec. These numbers are typical values for off-the-shelf devices and do not necessarily represent the state-of-the-art devices. In what follows, we consider two representative examples: • To demonstrate how network scheduler handles multi-job scenarios, we consider a stochastic sequence of random quantum circuits of varying size and depth. We construct random quantum circuits of _n_ qubits with a square form factor (equal width and depth). 

12 

**==> picture [254 x 216] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a)<br>(b)<br>1<br>2<br>3 [4]<br>**----- End of picture text -----**<br>


FIG. 6. Multi-job scheduling for jobs of identical size. (a) Job times (blue open and close circles) and rejection rates (green triangles), and (b) networked QPU usage (black dots) for a series of ~~r~~ andom jobs of equal size which arrive at random times according to a Poisson process (average rate is the request frequency). For each value of request frequency, a bar plot in (b) demonstrates the percentage of _n_ -QPU usage per rack on a ~~verage. This process is illustrated for one of th~~ e middle data points where the color coding for _n_ is also indicated. See Tabl ~~e I for network parameters.~~ 

- As a second example, we evaluate the network latency and compute infidelity for some common quantum algorithms which are often used as subroutines for more complex algorithms. 

## **A. Random benchmarks** 

In this experiment, we consider quantum jobs arriving at random times according to a Poisson distribution which is characterized by the number of jobs per unit time, _γ_ , called request frequency. In other words, the probability of having _k_ jobs over a period _t_ is given by ( _γt_ ) _[k] k_ ! _[e][−][γt]_[.] Our goal here is to generate network traffic (synthetically) and study how our design performs in terms of network latency in various scenarios. To this end, we consider random jobs in the form of random quantum circuits. We skip the compiler step for these jobs since such quantum circuits are featureless, i.e., all two-qubit gates are equally likely, and our simple qubit mapping algorithm will not have a a significant impact on average. 

We note that since we have a job queuing pipeline before sending jobs for the execution. Hence, we define two relevant quantities (which we collectively call job times) to capture the impact of network latency and multi-job execution: 

|Component<br>Switches|Figs.6, 7(a)<br>18|Figs.7(b),(c)<br>28|Table II<br>10|
|---|---|---|---|
|BSMs per switch<br>Racks<br>QPUs per rack<br>QPUs<br>Data qubits per QPU<br>Comm. qubits per QPU|4<br>9<br>4<br>36<br>10<br>4|4<br>16<br>8<br>128<br>10<br>4|2<br>4<br>4<br>16<br>20<br>4|



TABLE I. Number of various components in the quantum data center network with Clos topology _n_ = 6 studied in Secs. V A (Figs. 6 and 7) and V B (Table II). 

**Job completion time (JCT):** Time difference between the moment the job is finished and the moment the job is submitted. 

**Job execution time (JET):** Time takes to execute the quantum circuit from the moment the computation starts. 

Clearly, JCT for an accepted job is equal to the JET plus the buffer time. 

Table I summarizes the size of the network and number of various components used for simulations in this part. 

## _1. Equal job sizes_ 

In this experiment, we consider a sequence of random quantum circuits each with the same number of qubits such that each job is distributed across all racks utilizing one QPU per rack. Our motivation for coming up with such a choice is to create a synthetic traffic and congestion in the telecom layer of the Clos network in a controlled way so that we can interpret/understand the results easily. The number of various components are summarized in Table I. In particular, each job takes 90 qubits, and the circuit depth is equal to the circuit width. We run these jobs on a Clos network with 9 racks, and each rack has 4 QPUs. There are 10 data qubits per QPU. Hence, by design each job requires 9 QPUs which are distributed over all racks, and maximum number of parallel jobs is 4. We assume the job queue buffer size is 4, i.e., we only keep 4 jobs in the queue before sending them to the scheduling module; more jobs arriving will be rejected. 

Figure 6 shows how the performance metrics evolve as we increase the job arrival rate (or request frequency) from fewer than 1 job every 10 seconds to 10 jobs per second. For every request frequency, we compute JET and JCT, rejection rate, and the QPU usage as defined by 

**==> picture [224 x 23] intentionally omitted <==**

which is reported in percentage and used to capture how much of the QDC compute power is utilized for a given 

13 

request frequency. We further show a bar plot for each data point which illustrates QPU-resolved per rack usage i.e., out of the QPU percentage usage how much of it (in percentage) is 1 QPU per rack, 2 QPU per rack, etc. 

To obtain each data point in Fig. 6, we averaged these quantities over 10[3] iterations where each iteration is a time interval long enough that it contains 10[4] requests on average. As we move from left to right along the horizontal axis, when the request frequency is too small, we are at the single job scheduling regime where a given job finishes execution before the next job arrives. This results in identical values for the JET and JCT since there is no queuing time, which is about 2 _._ 3sec as we see in Fig. 6(a). This is also evident in Fig. 6(b), since QPU usage is very low (network is idle most of the time) and when in use it is nearly 100% of time operating at 1 QPU per rack (c.f. blue bars (b)). As we move past _γ_ = 4sec _[−]_[1] (corresponding to 4 jobs arriving every second), we start to have more overlapping jobs (i.e., we use more QPUs per rack as seen in bars other than blue), rising job times, and JCT and JET bifurcating (as queue is being formed). For higher request frequencies, then we utilize the entire resources (also 4 QPU per rack (red bar) is nearly 100%) and JET asymptotically reaches the four parallel job regime 5 _._ 1sec which is nearly twice as long compared to the single-job regime. Another way to see the job times plateauing is that QDC can only handle 4 jobs and the rest are sent to the queue. At the same time, because queue buffer has the capacity for 4 jobs then most requests are rejected. 

## _2. Variable job sizes_ 

Here, we present the results of two numerical experiments where random quantum circuits with different number of qubits arrive at various rates. In either experiments, our policy for QPU assignment in the waiting queue is FIFO provided that we meet the required number of QPUs, otherwise we check the subsequent jobs in the queue. Figure 6 summarizes the simulation results, where each data point is obtained by averaging over 10[3] iterations where each iteration is a time interval long enough that it contains 10[4] requests on average. 

As a first experiment, we consider jobs of different sizes in an incremental order each requiring _n_ = 2 _,_ 3 _, · · · ,_ 6 QPUs, respectively, arriving at the same rate. We show the job times for three request frequencies 0 _._ 1sec _[−]_[1] (i.e., one job every 10sec on average), 1sec _[−]_[1] (i.e., one job every second on average), and 10sec _[−]_[1] (i.e., 10 jobs every second on average) in Fig. 7(a). For slow request frequencies the average QPU occupancy is[�] _n_[= 20][which] is well below the total number of QPUs (c.f. Table I) and the job arrival times are well separated. Hence, the waiting queue almost always remains empty, and there is no difference between JET and JCT. We note that there is a clear jump in the JET as we go from 4(and below)-QPU jobs to 5(and above)-QPU jobs. The reason is jobs with 

4 or fewer QPUs are placed on the same rack and ebit generation is exclusively intra-rack at NIR frequencies, which are much faster than the inter-rack (telecom) ebit generation processes. 

The small difference between JCT and JET also holds for _γ_ = 1sec _[−]_[1] , since the slowest job is the one requiring 6 QPUs (which takes around 2sec to finish) and the network can accommodate two 6-QPU jobs (since during this 2sec on average two jobs of this type arrive). That said, we still observe an increase in job completion time due to more jobs running in parallel and sharing the network resources. 

When _γ_ = 10sec _[−]_[1] , we see that a large gap between JCT and JET develops as the queue is filling up. Aside from that, after a few rounds of QPU assignments, there will be random QPU availability across the racks. For example, there will be two or three empty QPUs which may not belong to the same rack and assigned to 2- or 3-QPU jobs. This leads to significantly longer execution times ( _T_ tot _∼_ 2sec) for such jobs compared to the the case with slower request frequencies ( _T_ tot _∼_ 100msec), where small jobs are mostly placed on the same rack. The reason is that quantum communications now run at telecom (inter-rack) which are significantly slower than the intra-rack communications. 

One may ask what would happen if there is a huge disparity between the job sizes. A typical scenario would be when large jobs are requested at slower rates and small jobs are requested at higher rates. This is studied in Fig. 7(b) and (c). Here, we consider three job sizes in the form of random quantum circuits requesting 4, 16, and 64 QPUs representing small, intermediate, and large jobs which are requested at different rates 10, 1, and 0 _._ 1 per sec, respectively. The data center is large enough to be able to accommodate two large jobs at the same time (c.f. Table I). For reference, we also show the corresponding values of JET and JCT when all job types arrive at the same rate _γ_ = 1sec _[−]_[1] . A (rather surprising) overall observation in Figs. 7(b) and (c) is that for small and intermediate jobs both JCT and JET are larger for uniform rates, while the order changes for the large jobs. We give an explanation below. 

The hierarchy in JCT is evident for non-uniform rates (orange bars) in Fig. 7(b) as there are more small or intermediate jobs in the queue (due to larger request frequencies) which will more likely be assigned faster (since they need fewer QPUs); however, we need to wait long enough until half of total QPUs become available for a large job. In contrast, when all job types have the same request frequency, we have similar number of different job sizes in the queue and the wait time for 64-QPU job drops significantly because they can replace an old 64-job which just finish executing. At the same time, there is a rise in the JCT of small and intermediate job sizes, i.e., they are kept longer in the queue, since they may not bypass a large job in the queue anymore. 

In contrast, the variation in JET for different job sizes (as shown in Fig. 7(c)) is not as much as that of JCT. 

14 

**==> picture [248 x 218] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a)<br>0.1 1 10<br>(b) (c)<br>**----- End of picture text -----**<br>


FIG. 7. Job completion times for multi-job scheduling of variable job sizes. In (a), the job sizes are incremental, and in (b) and (c) there are three job sizes of 4, 16, and 64 QPUs, which represent small, intermediate, and large job sizes, respectively. Horizontal black lines in (a) indicate the corresponding job execution times. 

An important observation is that although 4-QPU jobs can fit in a rack (which hosts 8 QPUs) JET of 4- and 16QPU jobs are fairly close. This is because 4-QPU jobs often share a rack with 16-QPU jobs and our scheduler distribute resources evenly between different jobs. As a result, 4-QPU job execution is slowed down by the neighboring 16-QPU job (which require intra-rack communications) with which it is sharing a rack. Compared to the uniform request rate, JETs are generally smaller when the rates are non-uniform because in the former case the odds of sharing resources with similar or greater jobs are higher which leads to an increased JET on average. 

## **B. Algorithmic benchmarks** 

We evaluate the proposed circuit compiler in Section IV A, which incorporates qubit assignment via graph partitioning and QPU assignment to racks using Integer Linear Programming (ILP), against a baseline of random qubit and QPU assignments. The comparison is conducted on several well-known benchmark circuits (studied in Ref. [73]), a Quantum Fourier Transform (QFT) circuit, and a Quantum Volume circuit for 100 qubits. 

Performance is assessed using two key metrics: Eq. (21) and job execution time, with results summarized in Table II. For random assignment, the results are averaged over 100 independent runs of the compiler. Overall, our analysis demonstrates that the proposed circuit-compiler consistently outperforms random assignment across all benchmarks and metrics, highlighting its 

||||
|---|---|---|
|Circuit<br>cnot<br>gates|Our compiler<br>Infd<br>Time[s]|Baseline|
|||Infd<br>Time[s]|
|BV (280)<br>152<br>QFT (100)<br>6510<br>QV (100)<br>15000<br>ISING (98)<br>194<br>ADDER (118)<br>845<br>CAT (260)<br>259<br>Swap (115)<br>456|1505<br>0.47<br>39470<br>20.31<br>107155<br>35.89<br>248<br>0.029<br>1236<br>0.54<br>345<br>0.033<br>2117<br>0.86|2130<br>0.71<br>68191<br>27.65<br>158242<br>40.10<br>2014<br>.42<br>9624<br>3.09<br>3164<br>.74<br>5716<br>1.97|



TABLE II. Performance metrics for algorithmic quantum circuits from [73]. Baseline is averaged quantities for random qubit/QPU assignments (see main text for details). The numbers in parenthesis denote the number of logical qubits in the circuit. Network parameters are provided in Table I. 

effectiveness in optimizing quantum circuit execution. 

In Table II, we observe the following trend: in general, the infidelity increases as the number of cnot gates increases. This can be explained as follows: even in the absence of non-local gates, the infidelity would still scale with the number of cnot gates, as indicated in Eq. (21). 

Examining the trends further, consider the BV(280) and ISING(98) circuits. Although the number of cnot gates in these circuits is approximately the same, the observed infidelity differs significantly. This discrepancy can be attributed to the number of non-local cnot gates, which is higher in the BV(280) circuit. In summary, the observed infidelity is influenced by two key factors: the total number of cnot gates and the fraction of those gates that are non-local. 

## **VI. DISCUSSION** 

In conclusion, this work introduces scalable architectures for quantum data center networks based on dynamic circuit-switched quantum networks that distribute entanglement between QPUs. By utilizing shared quantum resources and adopting modular topologies, such as switch-centric and server-centric designs, we achieve ondemand, all-to-all connectivity while minimizing reliance on costly quantum hardware. We developed a networkaware quantum orchestrator and entanglement generation protocols to manage distributed quantum computing jobs, connecting physical-layer architectures with quantum applications. Through simulations and benchmarking, we evaluate the circuit execution capabilities of our architectures, demonstrating the opportunities and challenges in scalability, efficiency, and fidelity. 

Our research establishes a foundation for the development of large-scale quantum computing infrastructure, bringing us closer to achieving practical quantum advantage. We have introduced novel quantum data center network architectures that go beyond traditional peer- 

15 

to-peer designs, opening up several avenues for future research. These architectures are not mutually exclusive but rather complementary, allowing for the combination of their strengths. For example, the inter-rack topology can be server-centric (as opposed to a star topology with a top-of-rack switch), while different racks can be connected using a switch-centric network. We have not yet explored the integration of quantum memories with optical switches in the network, which could offer more flexibility in terms of time synchronization and improved rates for seamless entanglement generation. Some initial efforts in this direction have been made by Choi _et al._ [74], who incorporated quantum memories into a fattree network topology. 

Throughout our paper, we adopt model abstractions and intentionally avoid delving deeply into the specifics of physical qubits, though our models are primarily inspired by cold atoms and trapped ions. While quantum hardware remains in its early stages and requires significant advancements to enable true large-scale quantum data centers, significant progress is being made. For instance, recent developments in photonic quantum technologies, such as nanofiber-based optical cavities serving as spin-photon interfaces, are laying the groundwork for scalable quantum data centers [7]. 

Moreover, while superconducting qubits have traditionally been the cornerstone for monolithic systems, notable progress has been achieved in distributed quantum computing between superconducting processors [40]. For example, our hybrid architecture could incorporate microwave-to-telecom transducers, such as those developed in Ref. [75]. Although current ebit generation rates with these transducers are quite low (around a few hundredths of a hertz), their integration demonstrates the feasibility of bridging various quantum platforms, highlighting the potential for future advancements. 

In our simulations, we accounted only for gate infidelity, neglecting the impact of qubit coherence time. While this approach is reasonable for highlighting that remote operations are significantly more error-prone than local quantum gates by assigning them lower fidelities, it overlooks a critical factor: data qubits used in quantum computation decohere over time. The extended duration of quantum communication between QPUs can significantly degrade computational quality due to qubit decoherence. This effect has not been included in our simulations. As shown in Sec. V, the computation time can span several seconds, which is comparable to the coherence time of various quantum technologies, particularly cold atoms and trapped ions. Consequently, it is essential to incorporate coherence time considerations into future analyses. 

In this paper, we focused on a near-term application where computations are performed on individual qubits. However, an additional intermediate layer could be introduced to the QDC network stack to enable entanglement distillation or, more generally, quantum error correction. In our study, we used ‘bare’ ebits as they were 

generated, without applying purification or error correction. While techniques like distillation or error correction can enhance fidelity, they incur additional costs in terms of time—leading to increased decoherence—and require more hardware resources. With quantum error correction, the network architecture may need to be adapted to include QPUs that utilize logical qubits (e.g., surface code). In such a setup, generating a logical ebit could involve producing _d_ physical ebits for a logical qubit encoded using a surface code of distance _d_ [76, 77]. In this context, exploring the trade-offs between simplicity and time efficiency in various ebit generation protocols, such as sequential versus parallel ebit generation, would be an interesting avenue for future research. 

To enable distributed quantum computing, we introduced the basic components of a quantum orchestrator designed to control quantum hardware and switches for executing jobs across a network. Our approach included a basic compiler with static circuit partitioning, where qubits are assigned at the outset, and inter-QPU gates are executed via gate teleportation. Future enhancements could involve advanced compilers with adaptive circuit partitioning [59–61]. The current circuit compiler necessitates an ebit count proportional to the number of remote gates, but number of necessary ebits can be reduced through compiler-based communication fusion [78, 79]. While our orchestrator employs sequential optimization steps, combining these into a holistic end-to-end optimization framework with feedback loops could offer greater efficiency. Such a framework would simultaneously consider qubit mapping, classical control signals, and other factors, likely resulting in complex nonlinear optimization problems. These challenges could be addressed with intelligent methods like reinforcement learning or genetic algorithms [80, 81], though these approaches are computationally intensive. Thus, developing effective heuristics remains a critical area for future work. 

In our numerical simulations, we primarily used random quantum circuits to remain agnostic to specific algorithm details. Specifically, we employed a Poisson process to model multi-job scheduling in our network orchestrator, simulating generic network traffic composed of random circuits. In the future, it would be valuable to define and study benchmarks or network traffic by categorizing quantum circuits based on their structural characteristics and utilizing representative benchmark sets derived from clustering similarly structured circuits [82]. 

Finally, the idea of integrating QPUs as accelerators within HPC infrastructures has gained significant attention recently [83]. Rather than replacing classical computers as general-purpose systems, quantum computers can excel at specialized tasks. Exploring the impact of our work on designing modular hybrid architectures—comprising multiple QPUs interconnected with classical HPC nodes—presents an exciting avenue for future research. On the orchestrator side, further advancements are needed to support seamless quantum-classical 

16 

integration, potentially leading to the development of future middleware systems [84]. 

**==> picture [60 x 9] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a) ∆ ! = 1GHz<br>**----- End of picture text -----**<br>


## **ACKNOWLEDGMENTS** 

The authors acknowledge insightful discussions with Stephen DiAdamo, Don Towsley, Yufei Ding, Luca Della Chiesa, Galan Moody, and Raj Jain. 

## **Appendix A: Simulations of scatterer-scatterer protocol** 

In this appendix, we numerically simulate the scatterer-scatterer protocol with probabilistic sources and present the statistics of success times. 

Our starting point is that an incoming photon wavepacket with mean characteristic time _ti_ is described by a Gaussian envelope function with the central frequency _ω_ 0 and linewidth of ∆ _ω_ 

**==> picture [239 x 30] intentionally omitted <==**

where _i_ is to denote the _i_ -th photons (could be presense/absence or time-bin). 

We now explain how we carry out the simulations step by step. A pseudo-code of our algorithm is given in Algorithm 1. We generate two random sequence of photon pair generation events associated with the two sources according to the Poisson distribution parameter _λ_ . Next, we find the pairs which are one after another and check if communication qubits are available (i.e., they are not undergoing reinitialization). If yes, we accept this event with probability 

**==> picture [202 x 21] intentionally omitted <==**

or reject with probability 1 _− p_ ss in which case the communication qubits go through a reinitialization (and will not be available for a duration of _τ_ 0). Here, the factor of 1 _/_ 2 is to account for the BSM success probability. Therefore, we observe that there is some finite probability for the coincidence as long as _|t_ 1 _− t_ 2 _|_ ∆ _ω_ ≲ 1. 

The above algorithm constitutes one iteration, and we must repeat this many times to accumulate some statistics. In Fig. 8, we show the tail distribution function (or complementary cumulative distribution function Pr( _X > x_ ) = 1 _−_ Pr( _X ≤ x_ )) of successful events after running 10[5] iterations where we only include iterations which end up with a successful events (since we are interested in the statistics of success time). 

We observe that the tail distribution aligns well with the exponential distribution described in Eq. (17), where the parameter _λ_ ss depends on system characteristics such as photon linewidth and qubit reinitialization time, 

**==> picture [197 x 204] intentionally omitted <==**

**----- Start of picture text -----**<br>
(b) ∆ ! = 3GHz<br>(c) ∆ ! = 10GHz<br>**----- End of picture text -----**<br>


FIG. 8. Tail distribution function of success time for scattererscatterer protocol for various qubit reinitialization times shown in the legend. Black solid lines are the fit according to the exponential distribution Pr( _T > t_ ) = _e[−][λ]_[ss] _[t]_ , (c.f. Eq. (17)). 

**==> picture [248 x 92] intentionally omitted <==**

FIG. 9. The fitted exponential distribution parameter as a function of photon linewidth and qubit reinitialization time. Legend in left (right) panel denotes the values of qubit reinitialization time (photon linewidth). 

as illustrated in Fig. 9. Generally, longer qubit reinitialization times or larger photon linewidths result in smaller rates _λ_ ss, leading to longer entanglement generation times. This is because entangled photons cannot be stored in communication qubits during reinitialization, and larger photon linewidths produce shorter photon wave packets with a reduced probability of overlap, as implied by Eq. (A2). 

17 

**Algorithm 1:** Simulating Entanglement generation protocol 

**==> picture [237 x 236] intentionally omitted <==**

**----- Start of picture text -----**<br>
input : Two lists of emission events P 1 and P 2.<br>output: Determine whether end-to-end entanglement<br>is realized or not, ebit =  True / False .<br>1 Combine P 1 and P 2 and sort them,<br>P =  sorted ( P 1 +  P 2).<br>2 Define control variables bool R 1 , R 2 :=  False whether<br>comm. qubits are undergoing resetting or not.<br>3 Define time when comm. qubits are available after<br>resetting float T 1 , T 2 := 0.<br>4 Initialize ebit =  False .<br>5 for pi, si ∈ P do<br>6 (pi, photon emission time, si, photon source)<br>7 If pi ≥ Tsi then Qsi =  False , Tsi = 0.<br>8 if si = si +1 (two consecutive photons belong to two<br>sources) then<br>9 If pi +1 ≥ Tsi +1 then Qsi +1 =  False , Tsi +1 = 0.<br>10 if Qsi =  Qsi +1 =  False then<br>11 ∆ t  =  pi +1  − pi .<br>12 Accept ebit with probability overlap (∆ t ),<br>ebit =  True , and exit .<br>13 If pi ≥ Tsi then Qsi =  True , Tsi =  pi  +  T reset.<br>14 return ebit.<br>**----- End of picture text -----**<br>


## **Appendix B: Additional network topologies** 

In this section, we present a few more network topologies for each category as explained below. The number of network switches, QPUs, and the network diameter are shown in Table III for reference [85]. 

is used across all three levels of the Fat-Tree. Moreover, high-performance switches are not required in the aggregation and core levels, making the Fat-Tree an efficient and scalable solution. 

A HyperX network [14] is a direct network of switches, where each switch connects to a fixed number _T_ of terminals. In general, a terminal can represent a compute node, a cluster of compute nodes, or any other interconnected device. In our case, we use terminals as top-of-rack (ToR) NIR switches. The switches are represented as points in an _L_ -dimensional integer lattice, with each switch uniquely identified by a coordinate vector _I_ = ( _I_ 1 _, . . . , IL_ ), where 0 _≤ Ik < Sk_ for each _k_ = 1 _, . . . , L_ . 

Within each dimension, the switches are fully interconnected. Consequently, each switch has bidirectional links to exactly[�] _[L] k_ =1[(] _[S][k][−]_[1)][other][switches,][connecting][to] all other switches that differ in only one coordinate. The total number of switches _P_ in the HyperX network satisfies _P_ =[�] _[L] k_ =1 _[S][k]_[.][A][regular][HyperX][network][is][defined] by the condition _Sk_ = _S_ for all _k_ , and is characterized by the tuple ( _L, S, K, T_ ). 

Figure 10(c) illustrates an example of an irregular HyperX topology with _L_ = 2, _S_ 1 = 2, _S_ 2 = 4, and _T_ = 3. In this case, there are two switches in the first dimension and four switches in the second dimension, forming an irregular HyperX structure. 

We note that the ToR switches connecting to QPUs in all three topologies shown in Figs. 10(a)-(c) are NIR switches. 

## **2. Server-centric topology** 

## **1. Switch-centric topology** 

A natural extension of the star topology (e.g., a topof-rack switch) is a simple tree structure, where switches are connected hierarchically, as illustrated in Fig. 10(a). However, this connectivity creates a performance bottleneck and introduces a single point of failure at the core level. To address these issues, the Fat-Tree topology [86] was proposed to enable non-blocking transmission. 

In a Fat-Tree topology, the links connecting nodes in adjacent tiers become progressively wider as they ascend the tree toward the root. This is accomplished by designing the topology such that, for any switch, the number of links connecting to its children equals the number of links connecting to its parent, assuming all links have the same capacity. In this configuration, each _n_ -port switch in the edge tier is connected to _n/_ 2 servers, while the remaining _n/_ 2 ports link to _n/_ 2 switches in the aggregation tier. Together, the _n/_ 2 aggregation switches, _n/_ 2 edge switches, and the servers form a basic unit of the Fat-Tree, referred to as a pod. At the core level, there are ( _n/_ 2)[2] _n_ -port switches, each connecting to all _n_ pods. Figure 10(b) depicts a Fat-Tree topology with _n_ = 4. Unlike the simple tree topology, the same type of switches 

A simplified yet more practical (for quantum network purposes) network architecture inspired by BCube is shown in Fig. 10(d), where neighboring racks are connected by optical switches. Because of the linear connectivity by design, we shall call it a linear network. This topology in the backbone is nothing but a linear repeater chain and we need to generate _n −_ 1 ebits to connect two QPUs from two racks with distance _n_ . However, this constraint can be improved by modifying the rack connectivities (but not all-to-all as in the case of BCube) such as the 2D network shown in Fig. 10(e) (which is kind of similar to the original work of Pant et al. [87]). 

Another example we consider is the DCell architecture[88], which can scale to very large number of interconnected QPUs using switches and QPUs with very few ports. The most basic element of a DCell, which is called DCell0, consists of _n_ QPUs and one _n_ -port switch. Each QPU in a DCell0 is connected to the switch in the same DCell0. The first step is to construct a DCell1 from several DCell0s. Each DCell1 has _n_ + 1 DCell0s, and each QPU of every DCell0 is connected to a QPU in another DCell1. As a result, the DCell0s are connected to each other, with exactly one link between every pair of DCell0s. A similar procedure 

18 

**==> picture [358 x 643] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a)<br>QPU1 QPU2 QPU3<br>(b)<br>QPU1 QPU2 QPU3 QPU4<br>(c)<br>(d)<br>QPU1 QPU2 QPU3 QPU4 QPU5 QPU6 QPU1 QPU2 QPU3 QPU4 QPU5 QPU6<br>(e) QPU1 QPU2 QPU1 QPU2 (f)<br>QPU3 QPU4 QPU3 QPU4<br>QPU1 QPU2<br>QPU3 QPU4<br>**----- End of picture text -----**<br>


FIG. 10. (a)-(c) Switch-centric network topologies: (a) Simple tree, (b) Fat-tree, and (c) HyperX. (d)-(f) Server-centric network topologies: (d) linear and (e) 2d networks introduced in this paper, and (f) DCell. 

19 

|||Switch-centric<br>Basic tree<br>Fat-tree<br>Clos network|Server-centric|
|---|---|---|---|
||||DCell<br>BCube|
|Diameter<br>No. of switches<br>No. of QPUs||2 log_n−_1_N_<br>6<br>6<br>_n_2+_n_+1<br>_n_3<br>_N_<br>5_N_<br>_n_<br>3<br>2_n_+ _n_2<br>4<br>(_n −_1)3<br>_n_3<br>4<br>_n_2<br>4 _× n_ToR|2_k_+1 _−_1<br>log_n N_<br>_N_<br>_n_<br>_N_<br>_n_ log_n N_<br>_≥_(_n_+ 1<br>2)2_k −_1<br>2<br>_≤_(_n_+ 1)2_k −_1<br>2<br>_nk_+1|



TABLE III. Summary of network parameters. _n_ is the number of outgoing ports of each switch to other switches or QPUs. For _n_ ToR specifically for Clos network denotes the number of QPUs per rack. _N_ is the total number of QPUs. Diameter is defined by the longest of shortest paths between QPUs. _k_ is the number of layers (or levels) in a server-centric network. 

is used to construct a DCell _k_ from several DCell _k−_ 1s. In a DCell _k_ , each QPU will eventually have _k_ + 1 links: the first link or the level-0 link connected to a switch when forming a DCell0, and level- _i_ link connected to a QPU in the same DCell _i_ but a different DCell _i−_ 1. Figure 10(f) shows a DCell1 when _n_ = 4. It can be seen that the number of QPUs in a DCell grows double-exponentially, and the total number of levels in a DCell is limited by the number of ports on the QPUs. For example, when _n_ = 6, _k_ = 3, a fully constructed DCell can comprise more than three million QPUs. 

As mentioned in the main text, the routing and scheduling of entanglement in server-centric topologies remains an open problem since it involves entanglement swapping in the intermediate QPUs. 

## **Appendix C: Rack assignment as ILP** 

In this appendix, we provide some details on how to formulate the QPU rack assignment problem as an integer linear program. This problem needs to be addressed after the circuit partitioning step in the compiler, where we still have a freedom of placing QPUs at different racks. Considering the hybrid architecture, we wish to minimize the number of inter-rack communications. 

We are to assign _N_ number of QPUs to _R_ number of racks such that the weighted number of remote gates (as defined below) are minimized. Our choice of objective is inspired by the estimated total circuit fidelity given by _F_ est. =[�] _i[F][ n] i[i]_ considering we have _M_ different types of gates labeled by _i_ = 1 _, · · · , M_ and _ni_ is the number of such gates. Upon taking the logarithm of this quantity we get a linear utility function 

**==> picture [167 x 30] intentionally omitted <==**

It is customary to consider one gate type as baseline (call it _i_ = 1) and define an objective function as a weighted sum as follows 

**==> picture [177 x 30] intentionally omitted <==**

which does not depend on the log base. For instance, for hybrid architectures we have two types of remote gates, intra-rack and inter-rack, 

**==> picture [246 x 36] intentionally omitted <==**

We note that the original utility function _U_ Fid is to be maximized, while the cost function _C_ Fid derived by dividing _U_ Fid by log _F_ 1 is to be minimized because log _F_ 1 _≤_ 0. In addition, since gate fidelities are close to one, they are often described by infidelities instead, _ϵi_ = 1 _− Fi ≪_ 1. In this case, we can approximate the log and define the objective function as 

**==> picture [169 x 30] intentionally omitted <==**

Here, we need to minimize the number of inter-rack communications by minimizing the objective function in Eq. (C3), where we shall drop _n_ loc term since it is a constant. To this end, we formulate the following integer linear programming problem 

**==> picture [236 x 64] intentionally omitted <==**

**==> picture [14 x 7] intentionally omitted <==**

**==> picture [217 x 65] intentionally omitted <==**

**==> picture [219 x 11] intentionally omitted <==**

**==> picture [219 x 11] intentionally omitted <==**

where _eij_ denote the number of remote gates between _i_ - th and _j_ -th QPUs, and our binary decision variables are _xir_ , a matrix indicating the rack assignment for QPU _i_ , i.e., _xir_ = 1 means QPU _i_ is placed at rack _r_ . In other 

20 

words, the _R_ -component vector _**x** i_ = ( _xi_ 1 _, · · · , xiR_ ) _[T]_ is a one-hot vector which indicates the location of the _i_ - th QPU. The one-hot vector condition is implemented by (C6). There are at most _n_ ToR spots at each rack, this constraint is implemented by (C7). We keep track of inter-rack remote gates by the variable _yijr_ which is calculated as an exclusive-or of the two vectors associated with _i_ -th and _j_ -th QPUs; i.e., _**y** ij_ as a vector contains all zeros if the two QPUs belong to the same rack, otherwise contains two non-zero entries. Finally, we use the one norm �� _**y** ij_ �� = � _r[y][ijr]_[to][count][the][number][of][inter-rack] and intra-rack remote gates. 

|Variable|Description|
|---|---|
|_Cq_<br>_Bs_<br>_Ms_<br>_Es_<br>_Ds_|Communication qubits<br>Ports on the beam splitter<br>BSM devices<br>Entanglement sources<br>Photon detectors|



TABLE IV. Notation used in ILP for the number of various network components. Subscripts _q_ and _s_ refer to QPUs and switches, respectively. 

Hence, the ILP is given by 

## **Appendix D: Resource management as ILP** 

In this appendix, we present an integer linear programming formulation of DQC routing or resource management. The general problem statement is as follows: Given a quantum circuit, find a sequence of gate executions which minimize the switching events and maximize the number of parallel ebit generations. 

The latter problem in general can be formulated as a multi-commodity max flow problem which can be implemented as an integer linear programming as we explain below. Minimizing switching events on the other hand, requires an algorithm which looks ahead (deeper) into the execution sequence which is more complex and out of the scope of the current work. 

We start with introducing some notations: Let _S_ = _S_ ToR _∪S_ C be the set of optical switches, which in turn can be decomposed into the top-of-rack _S_ ToR and core (telecom) _S_ C switches, respectively, _G_ be the set of remote two-qubit gates, which can similarly be decomposed as _G_ = _G_ ToR _∪G_ Int into the intra-rack (through top-of-rack) and inter-rack two-qubit gates. Finally, _Q_ = _{_ 1 _, · · · , N }_ denotes the set of QPUs. The rest of the system parameters are summarized in Table IV. 

As mentioned, we have two kinds of remote gates: inter-rack and intra-rack. For each inter-rack remote gate _g_ , we introduce a binary variable _x[g] p_[associated][with][a] path _p_ connecting the respective QPUs. Here, _p_ also includes the BSM to be used on that path. In other words, if there are _n_ switches equipped with BSM devices on path _p_ , we have _n_ number of variables _x[g] p_ 1 _[, x][g] p_ 2 _[,][ · · ·][, x][g] pn_[.] For each intra-rack remote gate _g_ , we consider another binary variable _y[g]_ which unlike the inter-rack gates does not have a associated path since there is only one shortest optical path through the top-of-rack switch. We note that if _y[g]_ = 1, it takes up one of the NIR BSMs on the corresponding ToR switch. 

The goal of ILP is to find a solution (assign values to _x[g] p_ and _y[g]_ ) by maximizing the number of ebits which can be generated in parallel. To this end, we define the objective function as a weighted sum over inter- and intra-rack paths where weight factors _w[g]_ can be used (as input) to implement some sort of gate priority in terms of their importance in the DAG (c.f. main text), or other factors. 

**==> picture [239 x 295] intentionally omitted <==**

We now go over the constraints. Eq. (D2) implies only one path per remote gate _g_ is required. Eq. (D3) imposes an upper bound on the number of paths connected to a QPU _q_ participating in gate _g_ because of the limited number of communication qubits _Cq_ . Eqs. (D4) and (D5) are required for intra-rack communications due to the number of ports on the beam splitters and NIR BSMs on ToR switches, respectively. To make sure there is no competition between the number of beam splitters and NIR BSMs, we can simply set _Bs_ = 2 _Ms_ and reduce these two constraints to one. Similarly, Eqs. (D6)-(D8) are required for inter-rack communications which impose constraints due to limited number of entanglement sources, photon detectors (for scatterers) and telecom BSM devices. 

In principle, we need to consider all possible paths between the QPUs which grows as _N_ ! with the number of QPUs. However, enumerating all paths is not useful in practice, since majority of paths are long and not 

21 

desirable. So, we can only limit ourselves to the set of shortest paths for each two-qubit gate. This is at the expense of more resource contention which leads to additional rounds of switching. Even limiting our solution into this smaller subspace of paths, the above ILP may 

- [1] A. S. Cacciapuoti, M. Caleffi, F. Tafuri, F. S. Cataliotti, S. Gherardini, and G. Bianchi, IEEE Network **34** , 137 (2019). 

- [2] M. Caleffi, M. Amoretti, D. Ferrari, D. Cuomo, J. Illiano, A. Manzalini, and A. S. Cacciapuoti, arXiv:2212.10609 (2022). 

- [3] D. Barral, F. J. Cardama, G. Díaz, D. Faílde, I. F. Llovo, M. M. Juane, J. Vázquez-Pérez, J. Villasuso, C. Piñeiro, N. Costas, J. C. Pichel, T. F. Pena, and A. Gómez, (2024), arXiv:2404.01265 [quant-ph]. 

- [4] R. Van Meter, R. Satoh, N. Benchasattabuse, K. Teramoto, T. Matsuo, M. Hajdusek, T. Satoh, S. Nagayama, and S. Suzuki, in _2022 IEEE International Conference on Quantum Computing and Engineering (QCE)_ (IEEE, 2022). 

- [5] S. Wehner, D. Elkouss, and R. Hanson, Science **362** , eaam9288 (2018). 

- [6] J. Liu and L. Jiang, IEEE Network , 1–1 (2024). 

- [7] S. Sunami, S. Tamiya, R. Inoue, H. Yamasaki, and A. Goban, arXiv:2407.11111 (2024). 

- [8] D. Cuomo, “Architectures and circuits for distributed quantum computing,” (2023), arXiv:2307.07908 [quantph]. 

- [9] B. He, D. Zhang, S. W. Loke, S. Lin, and L. Lu, IEEE Journal on Selected Areas in Communications **42** , 1919–1935 (2024). 

- [10] C. Monroe, R. Raussendorf, A. Ruthven, K. R. Brown, P. Maunz, L.-M. Duan, and J. Kim, Phys. Rev. A **89** , 022317 (2014). 

- [11] D. Earl, K. Karunaratne, J. Schaake, R. Strum, P. Swingle, and R. Wilson, “Architecture of a firstgeneration commercial quantum network,” (2022), arXiv:2211.14871 [quant-ph]. 

- [12] S. Gauthier, G. Vardoyan, and S. Wehner, in _Proceedings of the 1st Workshop on Quantum Networks and Distributed Quantum Computing_ (2023) pp. 38–44. 

- [13] C. E. Leiserson, IEEE Transactions on Computers **C-34** , 892 (1985). 

- [14] J. H. Ahn, N. Binkert, A. Davis, M. McLaren, and R. S. Schreiber, in _Proceedings of the Conference on High Performance Computing Networking, Storage and Analysis_ (2009) pp. 1–11. 

- [15] C. Guo, G. Lu, D. Li, H. Wu, X. Zhang, Y. Shi, C. Tian, Y. Zhang, and S. Lu, in _Proceedings of the ACM SIGCOMM 2009 conference on Data communication_ (2009) pp. 63–74. 

- [16] C. Clos, The Bell System Technical Journal **32** , 406 (1953). 

- [17] H. K. Beukers, M. Pasini, H. Choi, D. Englund, R. Hanson, and J. Borregaard, PRX Quantum **5** , 010202 (2024). 

- [18] T. Proctor, K. Young, A. D. Baczewski, and R. BlumeKohout, “Benchmarking quantum computers,” (2024), arXiv:2407.08828 [quant-ph]. 

- [19] E. Knill, D. Leibfried, R. Reichle, J. Britton, R. B. 

still remain degenerate and have many solutions due to symmetries of the network graph. We note that all these solutions are all equally acceptable since we already limit our search to the shortest paths. 

Blakestad, J. D. Jost, C. Langer, R. Ozeri, S. Seidelin, and D. J. Wineland, Physical Review A **77** (2008), 10.1103/physreva.77.012307. 

- [20] J. Helsen, I. Roth, E. Onorati, A. Werner, and J. Eisert, PRX Quantum **3** (2022), 10.1103/prxquantum.3.020357. 

- [21] J. Helsen and S. Wehner, “A benchmarking procedure for quantum networks,” (2021), arXiv:2103.01165 [quantph]. 

- [22] T. Lubinski, S. Johri, P. Varosy, J. Coleman, L. Zhao, J. Necaise, C. H. Baldwin, K. Mayer, and T. Proctor, (2023), arXiv:2110.03137 [quant-ph]. 

- [23] J. Laurat, “On-demand entanglement could lead to scalable quantum networks,” (2018). 

- [24] K. Chakraborty, F. Rozpedek, A. Dahlberg, and S. Wehner, arXiv:1907.11630 (2019). 

- [25] A. G. Iñesta and S. Wehner, Phys. Rev. A **108** , 052615 (2023). 

- [26] L. Talsma, Á. G. Iñesta, and S. Wehner, Physical Review A **110** , 022429 (2024). 

- [27] N. H. Lindner and T. Rudolph, Phys. Rev. Lett. **103** , 113602 (2009). 

- [28] V. S. Ferreira, G. Kim, A. Butler, H. Pichler, and O. Painter, Nature Physics , 1 (2024). 

- [29] Y. Zhan and S. Sun, Phys. Rev. Lett. **125** , 223601 (2020). 

- [30] H. Shapourian and A. Shabani, Quantum **7** , 935 (2023). 

- [31] H. Pichler, S. Choi, P. Zoller, and M. D. Lukin, Proceedings of the National Academy of Sciences **114** , 11362 (2017). 

- [32] S. Daiss, S. Langenfeld, S. Welte, E. Distante, P. Thomas, L. Hartung, O. Morin, and G. Rempe, Science **371** , 614 (2021). 

- [33] P. Lodahl, S. Mahmoodian, S. Stobbe, A. Rauschenbeutel, P. Schneeweiss, J. Volz, H. Pichler, and P. Zoller, Nature **541** , 473 (2017). 

- [34] M. L. Chan, Z. Aqua, A. Tiranov, B. Dayan, P. Lodahl, and A. S. Sørensen, Phys. Rev. A **105** , 062445 (2022). 

- [35] C. T. Nguyen, D. D. Sukachev, M. K. Bhaskar, B. Machielse, D. S. Levonian, E. N. Knall, P. Stroganov, R. Riedinger, H. Park, M. Lončar, and M. D. Lukin, Phys. Rev. Lett. **123** , 183602 (2019). 

- [36] M. K. Bhaskar, R. Riedinger, B. Machielse, D. S. Levonian, C. T. Nguyen, E. N. Knall, H. Park, D. Englund, M. Lončar, D. D. Sukachev, _et al._ , Nature **580** , 60 (2020). 

- [37] C. Knaut, A. Suleymanzade, Y.-C. Wei, D. Assumpcao, P.-J. Stas, Y. Huan, B. Machielse, E. Knall, M. Sutula, G. Baranes, _et al._ , Nature **629** , 573 (2024). 

- [38] S. Welte, B. Hacker, S. Daiss, S. Ritter, and G. Rempe, Phys. Rev. Lett. **118** , 210503 (2017). 

- [39] L. Jiang, J. M. Taylor, A. S. Sørensen, and M. D. Lukin, Physical Review A—Atomic, Molecular, and Optical Physics **76** , 062323 (2007). 

- [40] J. Ang _et al._ , ACM Transactions on Quantum Computing **5** (2024), 10.1145/3674151. 

- [41] W. P. Grice, Physical Review A—Atomic, Molecular, and 

22 

Optical Physics **84** , 042331 (2011). 

- [42] F. Ewert and P. van Loock, Physical review letters **113** , 140403 (2014). 

- [43] M. J. Bayerbach, S. E. D’Aurelio, P. van Loock, and S. Barz, Science Advances **9** , eadf4080 (2023). 

- [44] A. Orieux, M. A. Versteegh, K. D. Jöns, and S. Ducci, Reports on Progress in Physics **80** , 076001 (2017). 

- [45] D. Guo, _Data Center Networking_ , 1st ed. (Springer Nature, Singapore, 2022). 

- [46] T. van Leent, M. Bock, F. Fertig, R. Garthoff, S. Eppelt, Y. Zhou, P. Malik, M. Seubert, T. Bauer, W. Rosenfeld, _et al._ , Nature **607** , 69 (2022). 

- [47] U. Saha, J. D. Siverns, J. Hannegan, Q. Quraishi, and E. Waks, ACS Photonics **10** , 2861 (2023). 

- [48] E. Bersin _et al._ , PRX Quantum **5** , 010303 (2024). 

- [49] E. Bersin _et al._ , Physical Review Applied **21** , 014024 (2024). 

- [50] S. Muralidharan, L. Li, J. Kim, N. Lütkenhaus, M. D. Lukin, and L. Jiang, Scientific reports **6** , 20463 (2016). 

- [51] A. Abane, M. Cubeddu, V. S. Mai, and A. Battou, arXiv preprint arXiv:2408.01234 (2024). 

- [52] A. Dahlberg _et al._ , in _Proceedings of the ACM special interest group on data communication_ (2019) pp. 159– 173. 

- [53] W. Kozlowski, A. Dahlberg, and S. Wehner, in _Proceedings of the 16th international conference on emerging networking experiments and technologies_ (2020) pp. 1–16. 

- [54] M. Skrzypczyk and S. Wehner, arXiv preprint arXiv:2111.13124 (2021). 

- [55] C. Heunen and P. A. Martinez, Physical Review A **100** , 032308 (2019). 

- [56] B. W. Kernighan and S. Lin, The Bell System Technical Journal **49** , 291 (1970). 

- [57] G. Karypis and V. Kumar, SIAM Journal on Scientific Computing **20** , 359–392 (1998). 

- [58] D. Martyniuk, J. Jung, and A. Paschke, “Quantum architecture search: A survey,” (2024), arXiv:2406.06210 [quant-ph]. 

- [59] J. M. Baker, C. Duckering, A. Hoover, and F. T. Chong, in _Proceedings of the 17th ACM International Conference on Computing Frontiers_ (2020) pp. 98–107. 

- [60] F. Burt, K.-C. Chen, and K. Leung, arXiv preprint arXiv:2408.01424 (2024). 

- [61] E. Kaur _et al._ , In preparation (2024). 

- [62] J. Eisert, K. Jacobs, P. Papadopoulos, and M. B. Plenio, Phys. Rev. A **62** , 052317 (2000). 

- [63] L. Kamin, E. Shchukin, F. Schmidt, and P. van Loock, Phys. Rev. Res. **5** , 023086 (2023). 

- [64] Z. Yang, A. Ghubaish, R. Jain, H. Shapourian, and A. Shabani, AVS Quantum Science **6** (2024). 

- [65] S. Pouryousef, H. Shapourian, and D. Towsley, in _2024 International Conference on Quantum Communications, Networking, and Computing (QCNC)_ (IEEE, 2024) pp. 150–159. 

- [66] K. Goodenough, T. Coopmans, and D. Towsley, arXiv preprint arXiv:2404.07146 (2024). 

      - `ibm.com/api/qiskit/qiskit.dagcircuit.DAGCircuit` , accessed: 2024-11-13. 

   - [68] F. Hua, Y. Jin, Y. Chen, S. Vittal, K. Krsulich, L. S. Bishop, J. Lapeyre, A. Javadi-Abhari, and E. Z. Zhang, arXiv preprint arXiv:2211.01925 (2022). 

   - [69] G. Vardoyan and S. Wehner, arXiv preprint arXiv:2210.08135 (2022). 

   - [70] Y. Lee, W. Dai, D. Towsley, and D. Englund, (2022), arXiv:2210.10752 [quant-ph]. 

   - [71] Y. Zhou _et al._ , PRX Quantum **5** , 020307 (2024). 

   - [72] L. Stephenson _et al._ , Physical review letters **124** , 110501 (2020). 

   - [73] A. Li, S. Stein, S. Krishnamoorthy, and J. Ang, ACM Transactions on Quantum Computing **4** (2023), 10.1145/3550488. 

   - [74] H. Choi, M. G. Davis, Á. G. Iñesta, and D. R. Englund, arXiv preprint arXiv:2306.09216 (2023). 

   - [75] F. M. Mayor, S. Malik, A. G. Primo, S. Gyger, W. Jiang, T. P. Alegre, and A. H. Safavi-Naeini, arXiv preprint arXiv:2406.14484 (2024). 

   - [76] J. Ramette, J. Sinclair, N. P. Breuckmann, and V. Vuletić, npj Quantum Information **10** , 58 (2024). 

   - [77] J. Sinclair, J. Ramette, B. Grinkemeyer, D. Bluvstein, M. Lukin, and V. Vuletić, arXiv preprint arXiv:2408.08955 (2024). 

   - [78] A. Wu, Y. Ding, and A. Li, in _Proceedings of the 56th Annual IEEE/ACM International Symposium on Microarchitecture_ (2023) pp. 479–493. 

   - [79] A. Wu, H. Zhang, G. Li, A. Shabani, Y. Xie, and Y. Ding, in _2022 55th IEEE/ACM International Symposium on Microarchitecture (MICRO)_ (IEEE, 2022) pp. 1027–1041. 

   - [80] O. Crampton, P. Promponas, R. Chen, P. Polakos, L. Tassiulas, and L. Samuel, arXiv:2405.05875 (2024). 

   - [81] P. Promponas, A. Mudvari, L. Della Chiesa, P. Polakos, L. Samuel, and L. Tassiulas, arXiv:2404.17077 (2024). 

   - [82] M. Bandic, P. le Henaff, A. Ovide, P. Escofet, S. B. Rached, S. Rodrigo, H. van Someren, S. Abadal, E. Alarcon, C. G. Almudever, and S. Feld, “Profiling quantum circuits for their efficient execution on single- and multicore architectures,” (2024), arXiv:2407.12640 [quant-ph]. 

   - [83] M. Mohseni _et al._ , arXiv preprint arXiv:2411.10406 (2024). 

   - [84] N. Saurabh, S. Jha, and A. Luckow, “A conceptual architecture for a quantum-hpc middleware,” (2023), arXiv:2308.06608 [quant-ph]. 

   - [85] Y. Liu _et al._ , _Data center networks: Topologies, architectures and fault-tolerance characteristics_ (Springer Science & Business Media, 2013). 

   - [86] M. Al-Fares, A. Loukissas, and A. Vahdat, ACM SIGCOMM computer communication review **38** , 63 (2008). 

   - [87] M. Pant, H. Krovi, D. Towsley, L. Tassiulas, L. Jiang, P. Basu, D. Englund, and S. Guha, npj Quantum Information **5** , 25 (2019). 

   - [88] C. Guo, H. Wu, K. Tan, L. Shi, Y. Zhang, and S. Lu, in _Proceedings of the ACM SIGCOMM 2008 conference on Data communication_ (2008) pp. 75–86. 

- [67] “IBM qiskit DAGCircuit,” `https://docs.quantum.` 

