interface ContextSelectorProps {
    context: string;
    setContext: (context: string) => void;
  }
  
  const ContextSelector = ({ context, setContext }: ContextSelectorProps) => (
    <div className="mt-4">
      <select
        className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900"
        value={context}
        onChange={(e) => setContext(e.target.value)}
      >
        <option value="Onboarding">Onboarding</option>
        <option value="Support">Support</option>
        <option value="Feedback">Feedback</option>
      </select>
    </div>
  );
  
  export default ContextSelector;
  