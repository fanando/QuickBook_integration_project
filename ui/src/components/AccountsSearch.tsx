
import { useState, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import AccountsList from './AccountsList';
import useDebounce from '@/hooks/useDebounce';
import { getAccessToken, isTokenExpired } from '@/lib/localStorageUtils';
import { useToast } from '@/hooks/use-toast';

interface Account {
  Id: string;
  Name: string;
  AccountType: string;
  CurrentBalance: number;
  CurrencyRef?: {
    value: string;
    name: string;
  };
}

const AccountsSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const { toast } = useToast();

  useEffect(() => {
    
    const searchAccounts = async () => {
      const prefixParam = debouncedSearchTerm.trim()
      ? `?prefix=${encodeURIComponent(debouncedSearchTerm)}`
      : '';

      if (isTokenExpired()) {
        return;
      }

      try {
        setIsLoading(true);
        const accessToken = getAccessToken();
        const response = await fetch(
          `http://localhost:8000/accounts${prefixParam}`,
          {
            method:"GET",
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            }
          }
        );

        if (!response.ok) {
          if (response.status === 401) {
            toast({
              title: "Authentication Error",
              description: "Your session has expired. Please reconnect.",
              variant: "destructive"
            });
            return;
          }
          throw new Error('Failed to fetch accounts');
        }

        const data = await response.json();
        setAccounts(data);
      } catch (error) {
        console.error('Error searching accounts:', error);
        toast({
          title: "Error",
          description: "Failed to search accounts. Please try again.",
          variant: "destructive"
        });
        setAccounts([]);
      } finally {
        setIsLoading(false);
      }
    };

    searchAccounts();
  }, [debouncedSearchTerm]);

  const isDisabled = isTokenExpired();

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle>Search QuickBooks Accounts</CardTitle>
      </CardHeader>
      <CardContent>
        <Input
          placeholder="Search accounts by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="mb-4"
          disabled={isDisabled}
          aria-label="Search Accounts"
        />
        <AccountsList accounts={accounts} isLoading={isLoading} />
      </CardContent>
    </Card>
  );
};

export default AccountsSearch;
