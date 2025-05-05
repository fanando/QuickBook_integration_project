
import AuthButton from "@/components/AuthButton";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getTokens, isTokenExpired } from "@/lib/localStorageUtils";

const Index = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // If we have tokens and they're not expired, redirect to dashboard
    const tokens = getTokens();
    if (tokens && !isTokenExpired()) {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl mb-2">QuickBooks Dashboard Connect</CardTitle>
          <CardDescription>
            Connect your QuickBooks account to view and manage your financial data
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center">
          <AuthButton />
        </CardContent>
      </Card>
    </div>
  );
};

export default Index;
