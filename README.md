## Documeting all Industrialist recipies.

## What this is?

This is an effort to efficiently store recipe data for as many / all machines.

## What is the current effort?

This is just a passion project for me. So far, I am scraping the wiki for data for machines. So far I have the name and price at least of _almost_ every machine (The rest require to look into the exact text which I am not bothered to do just yet).

## The goal

The current goals are:

-   Name of each machine
-   Price of each machine
-   MF consumption and/or production of each machine
-   Connection inputs and outputs (Not location)
-   Size of machine
-   Pollution rate

Some of these are ambitious, but I believe this will be possible.

As this depends on the [wiki](https://industrialist.fandom.com/), this will depend on the wiki moderators updating it with accurate and up to date.

Sample snippet of data currently:

```json
"machine:/wiki/Large_Diesel_Engine": {
    "expires": 1766187811.91871,
    "value": {
        "name": "Large Diesel Engine",
        "attributes": {
            "Cost": "$1,000,000",
            "Size": "7x4",
            "Product (s)": "Power",
            "Pollution": "0.648%/h (normal)\n0.432%( Distilled Water )",
            "Output": "\u26a1 5MMF/s-6MMF/s",
            "Transfer Rate": "\u26a1 24MMF/s",
            "Capacity": "\u26a1 75MMF"
        },
        "sections": {},
        "recipies": [
        {
            "inputs": [
            {
                "link": "/wiki/Crude_Diesel",
                "amount": "20x"
            },
            {
                "link": "/wiki/Machine_Oil",
                "amount": "1x"
            }
            ],
            "outputs": [],
            "time": "10s",
            "energy": "-5MMF/s"
        },
        {
            "inputs": [
            {
                "link": "/wiki/Poor_Quality_Diesel",
                "amount": "15x"
            },
            {
                "link": "/wiki/Machine_Oil",
                "amount": "1x"
            }
            ],
            "outputs": [],
            "time": "10s",
            "energy": "-5MMF/s"
        },
        {
            "inputs": [
            {
                "link": "/wiki/Diesel",
                "amount": "10x"
            },
            {
                "link": "/wiki/Machine_Oil",
                "amount": "1x"
            }
            ],
            "outputs": [],
            "time": "10s",
            "energy": "-5MMF/s"
        },
        {
            "inputs": [
            {
                "link": "/wiki/Refined_Diesel",
                "amount": "7x"
            },
            {
                "link": "/wiki/Machine_Oil",
                "amount": "1x"
            }
            ],
            "outputs": [],
            "time": "10s",
            "energy": "-5MMF/s"
        }
        ]
    }
},
```
