
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

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

interface AccountsListProps {
  accounts: Account[];
  isLoading: boolean;
}

const AccountsList: React.FC<AccountsListProps> = ({ accounts, isLoading }) => {
  if (isLoading) {
    return (
      <div className="w-full py-8 text-center">
        <p className="text-gray-500">Loading accounts...</p>
      </div>
    );
  }

  if (!accounts || accounts.length === 0) {
    return (
      <div className="w-full py-8 text-center">
        <p className="text-gray-500">No accounts found. Try a different search term.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-[400px] w-full rounded-md border">
      <div className="p-4 space-y-4">
        {accounts.map((account) => (
          <Card key={account.Id} className="overflow-hidden">
            <CardContent className="p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-lg">{account.Name}</h3>
                  <p className="text-sm text-gray-500">{account.AccountType}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold">
                    {new Intl.NumberFormat('en-US', { 
                      style: 'currency', 
                      currency: account.CurrencyRef?.value || 'USD'
                    }).format(account.CurrentBalance)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </ScrollArea>
  );
};

export default AccountsList;
