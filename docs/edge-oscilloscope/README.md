# Edge Oscilloscope

The Edge Oscilloscope is an example application that can be downloaded for free from Siemens Industry Online Support (SIOS):
https://support.industry.siemens.com/cs/us/en/view/109808369

## Installation

First, download the Edge Oscilloscope app from SIOS.
Unzip the file, and extract the `.app` file.
Import the `.app` file into your IE Management Catalog via the `+ Import Application` button in top-right of the Catalog page.
Once imported into the Catalog, install the Edge Oscilloscope app onto your Edge Device.

If needed, you can modify the configuration file template during installation:

![Configuration Template](/images/install-config-file.png)

**NOTE**: databus credentials must be set this way.

## Configuration

With the exception of databus settings, all configuration of the Oscilloscope can be done from within the web browser app.

### Connections

After (re-)starting the Oscilloscope, the initial screen will be blank because no **Connection** has been selected:

![No Connection](/images/initial-screen.png)

Select a **Connection** from the drop-down list:

![Connection Selected](/images/connection-selected.png)

If no **Connections** are found, make sure you've specified the right **Metadata Topic** and that your databus credentials are correct.
Additionally, make sure that data is actually being published on that **Metadata Topic**.
This can be confirmed in Flow Creator, for example:

![Check Metadata](/images/metadata-flow-creator.png)

### Plot Settings

Once you've selected a **Connection**, you can adjust the plot settings in the configuration pane.
For example, to adjust the vertical scale of the plot, change the **Plot Height** parameter and click **Update**:

![Plot Height](/images/adjust-plot-height.png)

Similarly, to adjust the horizontal resolution of the plot, you can adjust the horizontal scale via the **Plot Width** parameter or the number of distinct datapoints shown via the **Plot Points** parameter:

![Plot Resolution](/images/adjust-plot-resolution.png)

## Operation

Once operational, you can simply monitor any signals of interest using the real-time waveform visualization (line chart) or use the audio recorder functionality in the bottom right to capture the signals into a `.wav` audio file.

### Recording

To begin recording, click **Start**; this will create a pop-up alert informing you that the recording is active:

![Start Recording](/images/start-recording.png)

Once you've collected sufficient data, click **Stop** to end the recording and **Download** to send the captured signals to your PC as a `.wav` file:

![Download Recording](/images/download-recording.png)

If you don't wish to download the recording, simply **Clear** it and begin again.

**NOTE**: to limit active memory consumption of the Oscilloscope, recordings are limited to 50MB each.
Any recording that runs longer than 50MB will be automatically split into multiple files.
In this case, on **Download**, all recordings will be downloaded together as a single `.zip` archive.

### Retrieve Files

In case you want to retrieve older recordings, you can visit the App Management tab of the Edge Device and see a full list of previous recordings:

![Retrieve Files](/images/view-app-files.png)

**NOTE**: to limit storage / disk usage of the Oscilloscope, the total number of recordings persisted on the disk is limited to 100 files (i.e., 5GB maximum).
