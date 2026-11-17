export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gradient-to-b from-green-50 to-emerald-100 text-slate-800">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-md border border-emerald-100 p-8 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-semibold uppercase tracking-wider">
          Stage 1: Initialized
        </div>
        
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-emerald-950">
          KrishiInsights
        </h1>
        
        <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
          An Agricultural Data Analytics and Crop Yield Intelligence Platform Using Machine Learning.
        </p>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-left text-sm space-y-2">
          <div className="flex justify-between items-center text-slate-700">
            <span className="font-medium">Frontend Environment:</span>
            <span className="text-emerald-700 font-semibold">Next.js (App Router) + TypeScript</span>
          </div>
          <div className="flex justify-between items-center text-slate-700">
            <span className="font-medium">Backend API Target:</span>
            <span className="text-emerald-700 font-semibold">FastAPI (Python)</span>
          </div>
          <div className="flex justify-between items-center text-slate-700">
            <span className="font-medium">Data Analytics:</span>
            <span className="text-emerald-700 font-semibold">Historical Indian Agricultural & IMD Rainfall Data</span>
          </div>
        </div>

        <p className="text-xs text-slate-400">
          Development environment verified. Ready for subsequent development stages.
        </p>
      </div>
    </main>
  );
}
