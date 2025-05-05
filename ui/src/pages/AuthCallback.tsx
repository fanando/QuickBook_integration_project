import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { saveTokens } from "@/lib/localStorageUtils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

const AuthCallback = () => {
  const [isProcessing, setIsProcessing] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  useEffect(() => {
    const processCallback = async () => {
      const urlParams = new URLSearchParams(location.search);
      const code = urlParams.get("code");
      const state = urlParams.get("state");
      const realmId = urlParams.get("realmId")

      if (!code || !state) {
        toast({
          title: "Authentication Failed",
          description: "Missing code or state from QuickBooks",
          variant: "destructive",
        });
        setIsProcessing(false);
        return;
      }
      

      try {
        const tokenRequest= await fetch (`http://localhost:8000/auth/callback?code=${code}&state=${state}&realmId=${realmId}`,
          {method:"GET"}
        )
        const tokenResponse = await tokenRequest.json();
        if (code) {
          saveTokens({
            access_token: tokenResponse.access_token,
            expiresIn:tokenResponse.expires_in,
          });

          toast({
            title: "Success",
            description: "Successfully connected to QuickBooks",
          });

          navigate("/dashboard");
        } else {
          throw new Error("Token data missing from response");
        }
      } catch (err) {
        console.error("Auth error:", err);
        toast({
          title: "Authentication Failed",
          description: "Something went wrong during authentication",
          variant: "destructive",
        });
        setIsProcessing(false);
      }
    };

    processCallback();
  }, [location, navigate, toast]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {isProcessing ? "Connecting to QuickBooks..." : "Authentication Failed"}
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          {isProcessing ? (
            <p>Please wait while we complete your authentication...</p>
          ) : (
            <>
              <p className="mb-4">There was a problem completing authentication.</p>
              <button
                onClick={() => navigate("/")}
                className="text-blue-600 hover:underline"
              >
                Return to Home
              </button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCallback;
