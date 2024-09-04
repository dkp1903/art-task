interface ActionButtonsProps {
    onCreateReport: () => void;
    onCallLead: () => void;
  }
  
  const ActionButtons = ({ onCreateReport, onCallLead }: ActionButtonsProps) => (
    <div className="flex flex-col space-y-2 mb-4">
      <button
        onClick={onCreateReport}
        className="px-4 py-2 bg-white text-purple-500 border border-purple-500 rounded-full text-sm font-medium hover:bg-gray-100"
      >
        Create Report this month
      </button>
      <button
        onClick={onCallLead}
        className="px-4 py-2 bg-white text-purple-500 border border-purple-500 rounded-full text-sm font-medium hover:bg-gray-100"
      >
        Call Lead
      </button>
    </div>
  );
  
  export default ActionButtons;
  