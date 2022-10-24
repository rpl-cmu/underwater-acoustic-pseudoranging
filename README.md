# underwater-acoustic-pseudoranging

## Acoustic Localization and Communication Using a MEMS Microphone for Low-cost and Low-power Bio-inspired Underwater Robots

[View the paper here.](https://arxiv.org/abs/2210.01089)

![GDOP and Results](/images/IROSGif3.gif)

This repository provides the code used to perform acoustic pseudoranging, as well as a few notes on hardware preparation and observations for future iterations. 

### Dependencies

The system runs on a raspberry pi using Python3. The following non-default packages are required:
* numpy
* librosa
* soundcard
* soundfile
* pyaudio

### Hardware setup

#### Transmitter side-

* Raspberry Pi 4 with a generic USB sound card allows 4 channel or more output to connected speakers. 
* Generic dual channel amplifiers are required to interface speakers to the soundcard
* Speakers can also be generic, we used the Lubell UW30 speakers which were the most cost effective, off the shelf option
* Speaker placement can be determined through a GDOP analysis in simulation

#### Receiver side-

* Raspberry Pi Zero W 
* Updating to RT-Preempt Kernel reduces latency in reading inbuilt Real-time clock. Recommended to perform, but not necessary 
* I2S ICS43434 microphone is connected. Wiring diagram is attached below. 
* 3D printed water tight boxes are used to house computation with the microphone top port on top, covered by a thin adhesive film, 1-2mm thick. The microphone has to be sealed with silicon glue to ensure water tightness. 

A cross sectional view of how we prepared the MEMS microphone for waterproofness is shown below.
![cross section](/images/cross-section.png)

More details on MEMS microphone waterpoofing using thin membranes and its effects can be found in this helpful [pdf link](https://invensense.tdk.com/wp-content/uploads/2015/02/Recommendations-for-Sealing-InvenSense-Bottom-Port.pdf) from invensense here.



#### Future improvements in design

* Using a different microcomputer capabale of using PCM inputs is ideal. These allow for higher sampling rates than I2S, making a wider range of audio signals possible. 
* Vesper MEMS systems also has several PCM and analog MEMS microphones which are water resistant. 
* Oil bladders are a way to wterproof mics which may allow them to work at deeper depths. Action cameras like GoPros use a waterproof diaphragm for each of their microphones. Applying a similar system would yield more effective waterproofing. 


### Some future directions for the algorithm

* State estimation using online filters
* 2 microphone system for bearing estimation along with location

