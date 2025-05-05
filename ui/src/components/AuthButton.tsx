
import { Button } from "@/components/ui/button";

const AuthButton: React.FC = () => {
  const handleConnect = async () => {
    try {
      window.location.href = 'http://localhost:8000/auth/authorize';
    } catch (error) {
      console.error('Failed to connect to QuickBooks:', error);
    }
  };

  return (
    <Button 
      onClick={handleConnect}
      className="bg-qb-blue hover:bg-qb-blue/90 text-white py-2 px-4 rounded-md shadow-md transition-colors"
    >
      Connect to QuickBooks
    </Button>
  );
};

export default AuthButton;
