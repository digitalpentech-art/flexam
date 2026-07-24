const SimulationPlugins = {
    'network_sim': {
        init: (containerId, initialState) => {
            console.log("Loading Network Sim:", initialState);
            document.getElementById(containerId).innerHTML = `
                <div class="p-4 border-2 border-dashed">
                    <h3>Virtual Network Lab</h3>
                    <button class="bg-green-600 text-white p-2" onclick="alert('Device Configured')">Configure Router</button>
                </div>
            `;
        }
    }
};

export default SimulationPlugins;
