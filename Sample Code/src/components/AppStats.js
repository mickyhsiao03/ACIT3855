import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [health, setHealth] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-kafka.eastus2.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    const getHealth = () => {
	
        fetch(`http://acit3855-kafka.eastus2.cloudapp.azure.com/health/health_status`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received health")
                setHealth(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);
    useEffect(() => {
		const interval = setInterval(() => getHealth(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getHealth]);

    if (error){
        return (
        <div className={"error"}>
            <p>Error found when fetching from API</p>
            <table className={"StatsTable"}>
                <tbody>
                    <tr>
                        <th>Service Status</th>
                    </tr>
                    <tr>
                        <td colspan="2">Receiver: {health['receiver']}</td>
                    </tr>
                    <tr>
                        <td colspan="2">Storage: {health['storage']}</td>
                    </tr>
                    <tr>
                        <td colspan="2">Processing: {health['processing']}</td>
                    </tr>
                    <tr>
                        <td colspan="2">Audit: {health['audit']}</td>
                    </tr>
                    <tr>
                        <td colspan="2">Last Updated: {health['last_updated']}</td>
                    </tr>
                </tbody>
            </table>
        </div>
                
        )
    }
    else if (isLoaded === false){
        return(<div>Loading...</div>)
    } 
    else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>stockNumber</th>
							<th>dateRange</th>
						</tr>
						<tr>
							<td>Count: {stats['num_stock']}</td>
							<td>Count: {stats['num_dRange']}</td>
						</tr>
						<tr>
							<td colspan="2">Top Stock Name: {stats['stock_name']}</td>
						</tr>
						<tr>
							<td colspan="2">Top Stock Number: {stats['stock_number']}</td>
						</tr>
						<tr>
							<td colspan="2">Top Stock Price: {stats['top_stock_price']}</td>
						</tr>
					</tbody>
                </table>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Service Status</th>
						</tr>
						<tr>
							<td colspan="2">Receiver: {health['receiver']}</td>
						</tr>
						<tr>
							<td colspan="2">Storage: {health['storage']}</td>
						</tr>
						<tr>
							<td colspan="2">Processing: {health['processing']}</td>
						</tr>
                        <tr>
							<td colspan="2">Audit: {health['audit']}</td>
						</tr>
                        <tr>
							<td colspan="2">Last Updated: {health['last_updated']}</td>
						</tr>
					</tbody>
                </table>
        
                
                
                {/* <h3>Last Updated: {stats['last_updated']}</h3> */}

            </div>
        )
    }
    
}
