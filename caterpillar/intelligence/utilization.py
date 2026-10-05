"""
Module 1: Utilization Calculation

Calculates the utilization percentage for an equipment asset.
Utilization = engine_hours / (engine_hours + idle_hours)
Handles division by zero.
"""


def calculate_utilization(asset):
    """
    Calculate utilization percentage for an equipment asset.

    Parameters:
    asset (dict): Asset dictionary with 'engine_hours_per_day' and 'idle_hours_per_day' keys

    Returns:
    float: Utilization percentage (0-100)
    """
    engine_hours = asset.get("engine_hours_per_day", 0)
    idle_hours = asset.get("idle_hours_per_day", 0)

    denominator = engine_hours + idle_hours

    if denominator == 0:
        return 0.0

    utilization = (engine_hours / denominator) * 100
    return round(utilization, 2)


# Example usage with the Caterpillar assets
if __name__ == "__main__":
    # EQX1001: Excavator, S003, engine=1.5, idle=10
    eqx1001 = {"engine_hours_per_day": 1.5, "idle_hours_per_day": 10}
    print(f"EQX1001 utilization: {calculate_utilization(eqx1001)}%")

    # EQX1007: Excavator, NULL, engine=0, idle=12
    eqx1007 = {"engine_hours_per_day": 0, "idle_hours_per_day": 12}
    print(f"EQX1007 utilization: {calculate_utilization(eqx1007)}%")