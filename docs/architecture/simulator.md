# Warehouse simulation assumptions

This is a synthetic discrete-event teaching model, not a calibrated warehouse digital twin. Orders move through reception, picking and dispatch queues; this simplifies actual replenishment and stock flows. Arrivals follow an exponential interarrival distribution. Service durations are synthetic functions of units and cartons. Winter uses five units per carton versus ten in summer and a larger carton handling coefficient. No employer data is used.

The shift stops at a fixed horizon. Backlog includes queued and in-service orders. Utilization counts service minutes clipped to the horizon, divided by available resource minutes. Cycle times cover completed orders only and may be biased by censoring. Wait totals cover operations that began service, not all outstanding jobs.

Use multiple seeds before drawing conclusions. A single scenario is not a causal estimate. Future work: independent random streams for paired comparisons, inventory/replenishment, shift calendars, validation with licensed public data, and optimization.
