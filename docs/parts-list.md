### A note about Pi availability

This project's goal is to run on a Raspberry Pi Zero 2W. Having the headers already installed is the easiest way to get the hat attached. I tried a hammer in header on my Pi Zero W and almost broke it, so I ordered a Pi Zero 2W with the headers pre-installed. If you want to actually pay MSRP, you might be able to find a Pi Zero 2WH on [rpilocator](https://rpilocator.com/). When I was first working on this project there wasn't one located in the US from the official vendors so I ended up getting one off Amazon instead [Pi Zero 2 WH with Pre-Soldered Color-Coded Header, Quad-Core 1GHz CPU, 512MB RAM, Wi-Fi & Bluetooth 4.2, Mini HDMI, 40 GPIO, CSI Camera Port](https://www.amazon.com/dp/B0DS68NPGF). If you ARE going to purchase a Pi off Amazon, or any retailer that isn't an official retailer, you do so at your own risk. My Pi Zero 2W from Amazon came in what looked like a legit anti-static bag with the proper labels and the Pi itself looks good, but that's a smple size of on.

The parts list below represents the links to the things I actually purchased.

## Parts List:
- [Pi Zero 2 WH with Pre-Soldered Color-Coded Header, Quad-Core 1GHz CPU, 512MB RAM, Wi-Fi & Bluetooth 4.2, Mini HDMI, 40 GPIO, CSI Camera Port](https://www.amazon.com/dp/B0DS68NPGF)
    - The cost off Amazon is almost DOUBLE MSRP, but that does include shipping in the price. I got "free" next day delivery with it, but YMMV on whether or not you get that; I'm pretty close to a major Amazon warehouse/hub
- [Coolwell Servo Driver HAT for for Raspberry Pi 4B+ 4B 3B+ 3B 2B+ Zero W WH Jetson Nano 16-Channel, 12-Bit, I2C Interface Right Angle Pinheader](https://www.amazon.com/dp/B0BS8PLYZC)
    - This did end up actually saying it's a Waveshare device on the screen printing of the hat, which is what I was hoping for
- [Miuzei MG90S 9G Micro Servo Motor Metal Geared Motor Kit for RC Car Robot Helicopter, Mini Servos for Arduino Project (2)](https://www.amazon.com/dp/B0BWJ4RKGV?th=1)
    - In the future I'm hoping to add a third servo to the project for coffee makers that need more than two buttons (ie for different cup sizes) so pick a different quantity than two if you need more than that
- [AC Adapter 9V 2A Power Supply AC110V to DC9V 2000mA 1500mA 1000mA 500mA Power Driver 8 DC Plug Tips 9 Volt Converter Inverter Charger Transformer ac dc Adapter](https://www.amazon.com/dp/B087ZWS7CG?th=1)
    - When I first started this project I was using linear solenoids and needed the extra voltage this could supply. I liked it because it had a barrel to screwdown adapter included for easy connectiong to VIN and GND on the Pi hat. You might be able to get away with the 6 volt, 2 amp version, but keep in mind we're using it to power the Pi Zero 2W AND the servos which can theoretically spike to about 1 AMP each, so we don't want to go below 2 amps.
- [LeMotech 5 Pieces ABS Plastic Electrical Project Case Power Junction Box, Project Box Black 3.5 x 2.8 x 1.1 inch (90 x 70 x 28 mm)](https://www.amazon.com/dp/B07QDWCL7M?th=1)
    - The jury is still out if this enclosure will work for prototyping as I haven't actually tried to shove stuff in it yet to test.