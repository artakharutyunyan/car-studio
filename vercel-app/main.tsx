/* Plain anchors support both the Vinext app and the standalone Vercel entry. */
/* eslint-disable next/no-html-link-for-pages */
import {createRoot} from 'react-dom/client';
import Garage from '../app/page';
import FormulaOne from '../app/formula-1/page';
import CarStudio from '../app/car-studio';
import {getAdjacentVehicles,getVehicle} from '../app/vehicles';
import '../app/globals.css';

const match=window.location.pathname.match(/^\/cars\/([^/]+)\/?$/);
const car=match?getVehicle(match[1]):undefined;
const {previous,next}=car?getAdjacentVehicles(car.id):{previous:undefined,next:undefined};
const page=window.location.pathname==='/'?<Garage/>:window.location.pathname.replace(/\/$/,'')==='/formula-1'?<FormulaOne/>:car?<CarStudio key={car.id} vehicle={car} previous={previous} next={next}/>:<main className="garage"><h1>Car not found</h1><a href="/">Back to the collection</a></main>;
createRoot(document.getElementById('root')!).render(page);
