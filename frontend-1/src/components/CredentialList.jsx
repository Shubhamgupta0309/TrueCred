import { useEffect, useState } from 'react';
import api from '../services/api';

export default function CredentialList() {
	const [items, setItems] = useState([]);
	const [busyId, setBusyId] = useState(null);
	const [message, setMessage] = useState(null);

	useEffect(() => {
		let active = true;
		const load = async () => {
			try {
				const res = await api.get('/credentials');
				if (!active) return;
				setItems(res.data?.data || res.data || []);
			} catch (e) {
				setMessage(e.message);
			}
		};
		load();
		return () => { active = false; };
	}, []);

	const prepare = async (id) => {
		try {
			setBusyId(id);
			const res = await api.post(`/blockchain/credentials/${id}/prepare`);
			setMessage(res.data?.message || 'Prepared');
		} catch (e) {
			setMessage(e.response?.data?.message || e.message);
		} finally {
			setBusyId(null);
		}
	};

	const store = async (id) => {
		try {
			setBusyId(id);
			const res = await api.post(`/blockchain/credentials/${id}/store`);
			setMessage(res.data?.message || 'Stored on-chain');
		} catch (e) {
			setMessage(e.response?.data?.message || e.message);
		} finally {
			setBusyId(null);
		}
	};

	const verify = async (id) => {
		try {
			setBusyId(id);
			const res = await api.get(`/blockchain/credentials/${id}/verify`);
			const ok = res.data?.data?.is_verified_on_blockchain;
			setMessage(ok ? 'Verified on-chain' : 'Not verified');
		} catch (e) {
			setMessage(e.response?.data?.message || e.message);
		} finally {
			setBusyId(null);
		}
	};

	return (
		<div className="space-y-3">
			{message && <div className="text-sm">{message}</div>}
			{items.length === 0 && <div className="text-sm text-gray-500">No credentials</div>}
			{items.map((c) => (
				<div key={c.id || c._id} className="rounded border p-3">
					<div className="font-medium">{c.title}</div>
					<div className="text-xs text-gray-500">{c.issuer}</div>
					<div className="mt-2 flex gap-2">
						<button disabled={busyId===c.id} onClick={() => prepare(c.id)} className="px-2 py-1 border rounded">Prepare</button>
						<button disabled={busyId===c.id} onClick={() => store(c.id)} className="px-2 py-1 border rounded">Store</button>
						<button disabled={busyId===c.id} onClick={() => verify(c.id)} className="px-2 py-1 border rounded">Verify</button>
					</div>
				</div>
			))}
		</div>
	);
}

