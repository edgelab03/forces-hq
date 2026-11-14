import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return <main className="not-found" id="main-content"><span className="eyebrow">FORCES HQ</span><h1>A little off course.</h1><p>This prototype contains Home and Ask. Let’s get you back.</p><Link className="primary-button" href="/"><ArrowLeft size={18}/>Back to Home</Link></main>;
}
