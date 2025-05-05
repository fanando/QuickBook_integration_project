
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AccountsSearch from "@/components/AccountsSearch";
import TokenExpiryMessage from "@/components/TokenExpiryMessage";
import { Button } from "@/components/ui/button";
import { isTokenExpired, clearTokens } from "@/lib/localStorageUtils";

const Dashboard = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Redirect to home if not authenticated
    if (isTokenExpired()) {
      navigate('/');
    }
  }, [navigate]);

  const handleDisconnect = () => {
    clearTokens();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-qb-text">QuickBooks Dashboard</h1>
            <TokenExpiryMessage />
          </div>
          <Button 
            variant="outline" 
            onClick={handleDisconnect}
            className="hover:bg-red-50 hover:text-red-600"
          >
            Disconnect
          </Button>
        </header>
        
        <main>
          <AccountsSearch />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
