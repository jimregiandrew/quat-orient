This file describes the data in this data directory.

# Data collection
I mounted my mobile phone, using Blu Tack, on the dash of our car, a Toyota Corolla. It was mounted square with the vehicle according to my eyecrometer. I used the AndroSensor Android app to collect gps and accelerometer for a 5 minute drive to "Granny's" place (2020-10-15-21) and for a trip back (2020-10-15-21). I converted AndroSensor's csv output to separate csv files: one for gps and one for accelerometer data. The format for the files is given in the csv header, with the convention that the timestamp (in milliseconds since trip start) is the first column.

The accelerometer (raw) data is 3-axis. The axes x,y and z I believe are those of Android's sensor coordinate system (See https://developer.android.com/guide/topics/sensors/sensors_overview#sensors-coords). That is with the screen vertical and facing you (default orientation) "the X axis is horizontal and points to the right, the Y axis is vertical and points up, and the Z axis points toward the outside of the screen face". How these axes relate to the vehicle's axes is the subject of this repository / open source algorithm, and depends on how the device is mounted in the vehicle.

# Data files
The files have format gps.date.csv and accel.date.csv for gps and accelerometer data respectively. The trips are delineated by date (and time if needed).
2020-10-15-21 - trip to Granny's
2020-10-15-22 - trip from Granny's

The GPS data can be overlaid on e.g. Google maps so the streets taken in each trip identified. I know these local (Aucland) streets well - e.g. their hills, corners, round-abouts etc. For example Ayr Street is on quite a steep hill, and approx 500m long. There is a round-about at the bottom. Shore road is mostly flat but there is one significant hill toward the Orakei Rd end.

# 2020-10-15-21.csv - trip to Granny's driving down Ayr St.
The first number per item is the timestamp in milliseconds since start of data recording. 

1. 63910 start of turning left into Ayr St.
2. 87792 middle of Ayr St (going down)
3. 110794 middle of round about at bottom of Ayr St
4. 127814 middle of left corner on Shore road, around Arney Rd intersection.
5. 170807 going uphill travelling past Stirling St.
6. 253805 going around the round-about in transition from Shore Rd to Orakei Rd.
7. 324799 turning right into Granny's driveway
8. 336805 stopped at Granny's.

The following timestamps are in seconds, and the annotation is using my eyecrometer with a Google maps GPS point visualization and acceleration plots.

## x accel relevant times
60-110 driving down Ayr St
160-180 driving up hill on Shore Rd towards Vicky Ave roundabout
200-230 sec driving downhill on Shore Rd past St Kents
245 slowing down for Shore/Orakei Rd roundabout
260 starting the climb up Orakei Rd
320-325 slowing down to turn into Granny's

## yaccel relevant times
65 turning left into Ayr St
105-111 round about at the bottom of Ayr St
134-138 right bend on shore Rd past the start of Thomas Bloodworth park carpark
154 left bend on shore road
226 left bend on Shore Rd
254 right turn on round about in transition from Shore Rd to Orakei Rd.

## Discussion
The accelerometer data matches up well with the gps data. That is braking, accelerating and cornering (left or right) acceleration according to the accelerometer is similar to the GPS derived acceleration, most of the time. But note the deviation is significant when there is significant road slope (in x and or y directions). e.g. on Ayr St. This is expected and one reason why accelerometer data is preferred to GPS derived acceleration data for driver behavior. Similarly, camber on corners, good or bad, is reflected in the accelerometer data, but not the GPS data.

# Slopes
Baldwin Street in Dunedin (New Zealand) at 16.33 degrees slope (2.75 m/s^2) is apparently too steep to park on. It is also the steepest street in the World.

Ayr Street (in Auckland) has an average gradient of 11.4% and a max of 12.9% according to https://veloviewer.com/segment/823851/Ayr+Street. 
This equates to an average of a 1.11 m/s^2 braking component from gravity, up to a maximum of 1.26 m/s^2
Note percent gradient is rise/run * 100 - where distance = sqrt(rise**2 + run**2).

2020-10-15-21 trip shows Ayr Street has somewhere in the range 1 - 1.5 m/s^2 slope. See qu.plot_faccel_gpsaccel('/home/jim/src/dbapp/','2020-10-15-21') in 
~/src/dbapp. That is there is a "dc" braking component of between 1 - 1.5 m/s^2 while travelling down Ayr Street.

(Google search: typical road crown) Road cant (road crown) ~1 - 2% on flat roads. Iowa dept. of transport advertises 4%.
1% == 0.1 m/s^2, and 4% == 0.4 m/s^2 (approx).

From my eyecrometer: altitude could possibly be used to improve the quaternion optimization. From 2020-10-15-21 you can see the altitude
change reflected in the "rolling average" of accel changing. I.e. a local accel mean x component becomes more -ve as we go down Ayr street. BUT it 
will probably worsen estimates in some cases - hard to know when ? (maybe if have heaps of satellites?)

