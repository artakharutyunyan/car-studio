import {notFound} from 'next/navigation';
import CarStudio from '../../car-studio';
import {getVehicle,vehicles} from '../../vehicles';

export function generateStaticParams(){return vehicles.map(car=>({slug:car.id}));}
export default async function VehiclePage({params}:{params:Promise<{slug:string}>}) {
  const {slug}=await params;
  const vehicle=getVehicle(slug);
  if(!vehicle)notFound();
  return <CarStudio key={vehicle.id} vehicle={vehicle}/>;
}
