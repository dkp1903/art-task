interface InputFieldProps {
    input: string;
    setInput: (input: string) => void;
    onSend: () => void;
    editingId: string | null;
  }
  
  const InputField = ({ input, setInput, onSend, editingId }: InputFieldProps) => (
    <div className="mt-4">
      <input
        type="text"
        placeholder="Your question"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900"
      />
      <button
        onClick={onSend}
        className="mt-2 w-full px-4 py-2 bg-purple-500 text-white rounded-lg"
      >
        {editingId ? 'Save' : 'Send'}
      </button>
    </div>
  );
  
  export default InputField;
  