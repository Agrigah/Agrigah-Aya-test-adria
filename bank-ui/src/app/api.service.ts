import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Toutes les requêtes passent par Spring Cloud Gateway
export const API = 'http://localhost:8080';

export interface Account { id: string; customerReference: string; status: 'ACTIVE' | 'BLOCKED'; currency: string; balance: number; }
export interface Transaction { id: string; accountId: string; amount: number; currency: string; merchantCategory?: string; country?: string; type: string; createdAt: string; }
export interface ChatResponse { conversationId: string; reply: string; }

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  accounts(): Observable<Account[]> { return this.http.get<Account[]>(`${API}/api/accounts`); }
  createAccount(b: { customerReference: string; currency: string; initialBalance: number }) {
    return this.http.post<Account>(`${API}/api/accounts`, b);
  }
  setStatus(id: string, status: string) { return this.http.patch<Account>(`${API}/api/accounts/${id}/status`, { status }); }

  transactions(accountId?: string): Observable<Transaction[]> {
    return this.http.get<Transaction[]>(`${API}/api/transactions`, { params: accountId ? { accountId } : {} });
  }
  createTransaction(b: object) { return this.http.post<Transaction>(`${API}/api/transactions`, b); }
  transfer(b: object) { return this.http.post(`${API}/api/transfers`, b); }

  chat(message: string, conversationId?: string) {
    return this.http.post<ChatResponse>(`${API}/api/chat`, { message, conversationId });
  }
}
