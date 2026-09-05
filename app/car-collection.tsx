/* Cards use pre-rendered, compressed WebP assets with explicit dimensions. */
/* eslint-disable next/no-img-element */
/* Plain anchors support both the Vinext app and the standalone Vercel entry. */
/* eslint-disable next/no-html-link-for-pages */
import {ArrowUpRight,Box} from 'lucide-react';
import {vehicles} from './vehicles';
import type {CSSProperties} from 'react';

export default function CarCollection({category='road'}:{category?:'road'|'formula-1'}) {
  const cars=vehicles.filter(car=>(car.category||'road')===category);
  const count=String(cars.length).padStart(2,'0');
  const racing=category==='formula-1';
  return <main className="garage">
    <header className="garage-header"><a href="/" className="garage-brand"><Box size={21} strokeWidth={1.3}/> CAR STUDIO</a><nav className="collection-nav" aria-label="Collections"><a href="/" aria-current={!racing?'page':undefined}>Road cars</a><a href="/formula-1" aria-current={racing?'page':undefined}>Formula 1</a></nav></header>
    <section className="garage-collection" aria-labelledby="collection-title">
      <div className="collection-heading"><div><p className="garage-eyebrow">{racing?'FORMULA 1 · THE RACING COLLECTION':'AN INTERACTIVE AUTOMOTIVE STUDY'}</p><h1 id="collection-title">{racing?'Built for the limit.':'Choose your perspective.'}</h1></div><p>{racing?'Explore the anatomy of a racing car.':'Every icon. Every angle.'}<br/>{racing?'Select a car to enter the studio.':'Select a car to explore its anatomy.'}</p></div>
      <div className="car-grid">{cars.map((car,index)=><a className="car-card" href={`/cars/${car.id}`} key={car.id} style={{'--car-accent':car.paint} as CSSProperties} aria-label={`Explore ${car.make} ${car.name}`}>
        <div className="car-card-top"><span>{String(index+1).padStart(2,'0')} / {count}</span><span><i/>{car.color}</span></div>
        <div className="car-card-image"><img src={car.image} alt={`${car.color} ${car.make} ${car.name} in the studio`} width={960} height={720} loading={index<3?'eager':'lazy'}/></div>
        <div className="car-card-content"><p className="car-make">{car.make}</p><h2>{car.name}</h2><p className="car-edition">{car.edition}</p><div className="car-card-footer"><span>Explore in 3D</span><span className="car-card-arrow"><ArrowUpRight size={21} strokeWidth={1.5}/></span></div></div>
      </a>)}</div>
    </section>
    <footer className="garage-footer"><span>ORBIT. ISOLATE. EXPLORE.</span><span>An independent study of automotive design.</span></footer>
  </main>;
}
