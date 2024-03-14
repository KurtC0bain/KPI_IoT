from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

interval = {
    "normal": {
        "start": 14000, 
        "end": 18000
        },
    "less": {
        "start": 12000, 
        "end": 14000
        },
    "greater": {
        "start": 18000, 
        "end": 20000
        }
}


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    # Implement it
    # Assuming classification logic based on accelerometer z-axis value ranges
    z_acceleration = agent_data.accelerometer.z

    if interval["normal"]["start"] > z_acceleration < interval["normal"]["end"]:
        road_state = "normal"
    elif interval["less"]["start"] > z_acceleration < interval["less"]["end"] or interval["greater"]["start"] > z_acceleration < interval["greater"]["end"]:
        road_state = "small pits"
    else:
        road_state = "large pits"
    return ProcessedAgentData(road_state=road_state, agent_data=agent_data)