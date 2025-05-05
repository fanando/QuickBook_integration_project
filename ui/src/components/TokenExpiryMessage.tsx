
import { useEffect, useState } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { isTokenExpired, getExpiryTime } from '@/lib/localStorageUtils';

interface TokenExpiryMessageProps {
  showExpiry?: boolean;
}

const TokenExpiryMessage: React.FC<TokenExpiryMessageProps> = ({ showExpiry = true }) => {
  const [isExpired, setIsExpired] = useState<boolean>(false);
  const [expiryTime, setExpiryTime] = useState<Date | null>(null);

  useEffect(() => {
    // Check if token is expired
    setIsExpired(isTokenExpired());
    setExpiryTime(getExpiryTime());

    // Set up interval to check expiration every minute
    const intervalId = setInterval(() => {
      setIsExpired(isTokenExpired());
    }, 60000);

    return () => clearInterval(intervalId);
  }, []);

  if (isExpired) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertDescription className="text-center">
          Your session has expired. Please reconnect.
        </AlertDescription>
      </Alert>
    );
  }

  if (showExpiry && expiryTime) {
    const formattedTime = expiryTime.toLocaleString();
    
    return (
      <div className="text-sm text-gray-500 mb-4">
        Token expires at: {formattedTime}
      </div>
    );
  }

  return null;
};

export default TokenExpiryMessage;
