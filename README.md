Welcome to the repository for SubArc: An Inexpensive, High Resolution, Open Source, Absolute Magnetic Rotary Encoder!

In this repository, there are the files for the 3D models of the most recent SubArc PCB and Calibration Stand version. There are the SubArc python executable programs and the microcontroller (Arduino standard) code. Additionally, a specification sheet, a mounting tutorial, and other in-depth documentation are also listed.

At this time, SubArc is still under development. That being said, the current SubArc version does output 20 bit resolution at under 150 arc seconds of average accuracy, and can be vigilantly used for low-speed applications. 

The following improvements are being made to release an initial beta-version of SubArc (with the goal being by March 2026):

1) Fix occasional accuracy spike bugs
2) Increase position calibration file search algorithm efficiency
3) Increase sampling rate to 5000 Hz with updated hall sensor array
4) Create through-bore version to easy mounting on machinery

Once these improvements are made and SubArc properly functions embedded on precision machinery technology, SubArc will release into its V1 beta version and this repository will be linked and popularized.

If you would like to build your own SubArc and need assistance, or you would like to collaborate on speeding up the development to the initial beta-version, feel free to contact me at: franklucci636@gmail.com

This work is provisional-patent protected to ensure no one attempts to patent and close source this encoder. All current and future work will continue to be open source under the MIT license.

Current SubArc specification details:

You can customize the SubArc ring and readhead in your PCB software to change the resolution and accuracy

Standard resolution is 20-bits, with an 8mm bore, 55mm diameter, 100 magnets, and 6 hall sensors
