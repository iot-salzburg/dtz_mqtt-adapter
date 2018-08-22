# Create SensorThings instances

for each using the POST method


## Thing

http://il081:8084/v1.0/Things

{
   "name": "Prusa i3",
   "description": "3D Printer Prusa i3 MK3 in the Iot Lab Salzburg on the central desk",
   "properties": {
      "kafka": {
         "hosts": [
            "il081:9093",
            "il082:9094",
            "il083:9095"
         ],
         "topics": {
            "logs": "dtz-logging",
            "metrics": "dtz-sensorthings"
         },
      "specification": "https://www.prusa3d.com/downloads/manual/prusa3d_manual_175_en.pdf"
      }
}

{
  "name": "Panda",
  "description": "Franka Emika Panda robot in the Iot Lab Salzburg on the central desk",
  "properties": {
    "specification": "https://s3-eu-central-1.amazonaws.com/franka-de-uploads-staging/uploads/2018/05/2018-05-datasheet-panda.pdf"
  }
}


## Location

for each Thing:

http://il081:8084/v1.0/Things(1)/Locations

http://il081:8084/v1.0/Things(2)/Locations

{
  "name": "IoT Labor Salzburg",
  "description": "IoT Labor of Salzburg Research",
  "encodingType": "application/vnd.geo+json",
  "location": {
    "type": "Point",
    "coordinates": [13.040670, 47.822784]
  }
}



## Sensor

http://il081:8084/v1.0/Sensors

{
  "name": "prusa internal temp sensor",
  "description": "Internal temperature sensor of the Prusa i3 3D Printer",
  "encodingType": "application/pdf",
  "metadata": "https://www.prusa3d.com/downloads/manual/prusa3d_manual_175_en.pdf"
}

{
  "name": "prusa internal controller",
  "description": "Derived Output from the internal controller of the Prusa i3 3D Printer",
  "encodingType": "application/pdf",
  "metadata": "https://www.prusa3d.com/downloads/manual/prusa3d_manual_175_en.pdf"
}


## Datastreams with Observed Properties

http://il081:8084/v1.0/Datastreams

### Temperature Data
{
  "name": "Target Bed Temperature Prusa",
  "description": "Datastream for the target temperature of the Prusa 3D printer's bed",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
  "unitOfMeasurement": {
    "name": "Degree Celsius",
    "symbol": "degC",
    "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius"
  },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
      {
      "name": "Target Bed Temperature of the Prusa i3",
      "description": "The desired temperature of the Prusa i3's printing bed",
      "definition": "http://www.qudt.org/qudt/owl/1.0.0/quantity/Instances.html#AreaTemperature"
        },
  "Sensor":{"@iot.id":1}
}


{
  "name": "Actual Bed Temperature Prusa",
  "description": "Datastream for the measured temperature of the Prusa 3D printer's bed",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
  "unitOfMeasurement": {
    "name": "Degree Celsius",
    "symbol": "degC",
    "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius"
  },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "Actual Bed Temperature of the Prusa i3",
      "description": "The measured temperature of the Prusa i3's printing bed",
      "definition": "http://www.qudt.org/qudt/owl/1.0.0/quantity/Instances.html#AreaTemperature"
    },
  "Sensor":{"@iot.id":1}
}


{
  "name": "Target Nozzle Temperature Prusa",
  "description": "Datastream for the target temperature of the Prusa 3D printer's nozzle",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
  "unitOfMeasurement": {
    "name": "Degree Celsius",
    "symbol": "degC",
    "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius"
  },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "Target Nozzle Temperature of the Prusa i3",
      "description": "The desired temperature of the Prusa i3's nozzle",
      "definition": "http://www.qudt.org/qudt/owl/1.0.0/quantity/Instances.html#AreaTemperature"
    },
  "Sensor":
    {
      "name": "prusa internal temp sensor",
      "description": "Internal temperature sensor of the Prusa i3 3D Printer",
      "encodingType": "application/pdf",
      "metadata": "https://www.prusa3d.com/downloads/manual/prusa3d_manual_175_en.pdf"
    }
}


{
  "name": "Actual Nozzle Temperature Prusa",
  "description": "Datastream for the measured temperature of the Prusa 3D printer's nozzle",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
  "unitOfMeasurement": {
    "name": "Degree Celsius",
    "symbol": "degC",
    "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius"
  },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "Actual Nozzle Temperature of the Prusa i3",
      "description": "The measured temperature of the Prusa i3's nozzle",
      "definition": "http://www.qudt.org/qudt/owl/1.0.0/quantity/Instances.html#AreaTemperature"
    },
  "Sensor":
    {
      "name": "prusa internal temp sensor",
      "description": "Internal temperature sensor of the Prusa i3 3D Printer",
      "encodingType": "application/pdf",
      "metadata": "https://www.prusa3d.com/downloads/manual/prusa3d_manual_175_en.pdf"
    }
}


### Processing Data

{
  "name": "Processing information",
  "description": "Datastream for the internal processings",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
  "unitOfMeasurement": {
    "name": "processing information",
    "symbol": "srfg.prusa3d.processing",
    "definition": "json-message"
      },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "processing data",
      "description": "processes run to perform a print (printing, slicing)",
      "definition": "srfg.prusa3d.processing"
    },
  "Sensor":{"@iot.id":5}
}

### MQTT status

{
  "name": "mqtt connection status",
  "description": "Datastream for the mqtt network connection",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
  "unitOfMeasurement": {
    "name": "mqtt connection status",
    "symbol": "srfg.prusa3d.mqtt",
    "definition": "connection-status"
      },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "network information",
      "description": "mqtt network connection of the printer's controller",
      "definition": "srfg.prusa3d.mqtt"
    },
  "Sensor":{"@iot.id":5}
}


### Prusa events

{
  "name": "prusa events",
  "description": "Datastream for printing events",
  "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
  "unitOfMeasurement": {
    "name": "printing event",
    "symbol": "srfg.prusa3d.event",
    "definition": "json-message"
      },
  "Thing":{"@iot.id":1},
  "ObservedProperty":
    {
      "name": "event information",
      "description": "events occurring while printing",
      "definition": "srfg.prusa3d.event"
    },
  "Sensor":{"@iot.id":5}
}