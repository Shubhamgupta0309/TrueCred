import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function BlockchainStatus() {
	const [info, setInfo] = useState(null);
	const [error, setError] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		let active = true;
		const fetchInfo = async () => {
			try {
				setLoading(true);
				const res = await api.get('/blockchain/status');
				const data = res.data;
				if (!active) return;
				const connected = Boolean(data.web3_connected) && Boolean(data.contract_loaded || data.contract_address);
				setInfo({
					connected,
					network: data.network,
					chain_id: data.chain_id || data.deployment_info?.chainId,
					contract_loaded: Boolean(data.contract_loaded || data.contract_address),
					contract_address: data.contract_address
				});
			} catch (e) {
				if (!active) return;
				setError(e.message);
			} finally {
				if (active) setLoading(false);
			}
		};
		fetchInfo();
		return () => { active = false; };
	}, []);

	if (loading) return <div className="text-sm text-gray-500">Checking blockchain status…</div>;
	if (error) return <div className="text-sm text-red-600">{error}</div>;
	if (!info) return null;

	return (
		<div className="rounded-md border p-3 text-sm">
			<div className="font-medium">Blockchain</div>
			<div className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1">
				<div className="text-gray-500">Connected</div>
				<div>{info.connected ? 'Yes' : 'No'}</div>
				<div className="text-gray-500">Network</div>
				<div>{info.network ?? '-'}</div>
				<div className="text-gray-500">Chain ID</div>
				<div>{info.chain_id ?? '-'}</div>
				<div className="text-gray-500">Contract loaded</div>
				<div>{info.contract_loaded ? 'Yes' : 'No'}</div>
				<div className="text-gray-500">Contract address</div>
				<div className="truncate">{info.contract_address ?? '-'}</div>
			</div>
		</div>
	);
}

