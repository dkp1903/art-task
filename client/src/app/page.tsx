"use client";
import Image from "next/image";
import Chat from './components/Chat'

export default function Home() {
  return (
    <div className="container mx-auto">
      <Chat />
    </div>
  );
}
