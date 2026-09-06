'use client';
/* Cards use pre-rendered, compressed WebP assets with explicit dimensions. */
/* eslint-disable next/no-img-element */
/* Plain anchors support both the Vinext app and the standalone Vercel entry. */
/* eslint-disable next/no-html-link-for-pages */
import {ArrowUpRight, Search, X} from 'lucide-react';
import {useMemo, useState} from 'react';
import {vehicles} from './vehicles';
import type {CSSProperties} from 'react';

export default function CarCollection({category='road'}:{category?:'road'|'formula-1'}) {
  const [query,setQuery]=useState('');
  const racing=category==='formula-1';
  const cars=useMemo(()=>{
    const q=query.trim().toLowerCase();
    return vehicles
      .filter(car=>(car.category||'road')===category)
      .filter(car=>!q || `${car.make} ${car.name} ${car.edition}`.toLowerCase().includes(q))
      .sort((a,b)=>`${a.make} ${a.name}`.localeCompare(`${b.make} ${b.name}`));
  },[category,query]);
  const count=String(cars.length).padStart(2,'0');
  return <main className="garage">
    <header className="garage-header"><a href="/" className="garage-brand"><img src="/brand/car-studio-icon.png" width={36} height={36} alt=""/> CAR STUDIO</a><nav className="collection-nav" aria-label="Collections"><a href="/" aria-current={!racing?'page':undefined}>Road cars</a><a href="/formula-1" aria-current={racing?'page':undefined}>Formula 1</a></nav></header>
    <section className="garage-collection" aria-labelledby="collection-title">
      <div className="collection-heading"><div><p className="garage-eyebrow">{racing?'FORMULA 1 · THE RACING COLLECTION':'AN INTERACTIVE AUTOMOTIVE STUDY'}</p><h1 id="collection-title">{racing?'Built for the limit.':'Choose your perspective.'}</h1></div><p>{racing?'Explore the anatomy of a racing car.':'Every icon. Every angle.'}<br/>{racing?'Select a car to enter the studio.':'Select a car to explore its anatomy.'}</p></div>
      <div className="collection-search"><Search size={16}/><input type="text" value={query} onChange={e=>setQuery(e.target.value)} placeholder={racing?'Search Formula 1 cars…':'Search road cars…'} aria-label="Search cars"/>{query&&<button type="button" onClick={()=>setQuery('')} aria-label="Clear search"><X size={15}/></button>}</div>
      {cars.length?<div className="car-grid">{cars.map((car,index)=><a className="car-card" href={`/cars/${car.id}`} key={car.id} style={{'--car-accent':car.paint} as CSSProperties} aria-label={`Explore ${car.make} ${car.name}`}>
        <div className="car-card-top"><span>{String(index+1).padStart(2,'0')} / {count}</span><span><i/>{car.color}</span></div>
        <div className="car-card-image"><img src={car.image} alt={`${car.color} ${car.make} ${car.name} in the studio`} width={960} height={720} loading={index<3?'eager':'lazy'}/></div>
        <div className="car-card-content"><p className="car-make">{car.make}</p><h2>{car.name}</h2><p className="car-edition">{car.edition}</p><div className="car-card-footer"><span>Explore in 3D</span><span className="car-card-arrow"><ArrowUpRight size={21} strokeWidth={1.5}/></span></div></div>
      </a>)}</div>:<p className="collection-empty">No cars match “{query}”.</p>}
    </section>
    <footer className="garage-footer"><span>ORBIT. ISOLATE. EXPLORE.</span><span>An independent study of automotive design.</span></footer>
  </main>;
}
