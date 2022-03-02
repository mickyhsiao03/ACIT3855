import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-kafka.eastus2.cloudapp.azure.com:8100/stats`)
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
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
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
                {/* <h3>Last Updated: {stats['last_updated']}</h3> */}

            </div>
        )
    }
}
