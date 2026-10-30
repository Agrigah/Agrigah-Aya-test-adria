import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Account, ApiService, Transaction } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  tab: 'accounts' | 'transaction' | 'transfer' | 'chat' = 'accounts';
  accounts: Account[] = [];
  transactions: Transaction[] = [];
  selectedAccountId = '';
  message = '';
  error = '';

  newAccount = { customerReference: '', currency: 'EUR', initialBalance: 0 };
  tx = { accountId: '', amount: 100, currency: 'EUR', merchantCategory: 'GROCERY', country: 'MA', type: 'DEBIT' };
  tr = { fromAccountId: '', toAccountId: '', amount: 100, currency: 'EUR' };

  chatInput = '';
  conversationId?: string;
  chatLog: { from: 'me' | 'bot'; text: string }[] = [];
  chatBusy = false;

  constructor(private api: ApiService) {}

  ngOnInit() { this.refresh(); }

  refresh() {
    this.api.accounts().subscribe({ next: a => { this.accounts = a; this.error = ''; }, error: e => this.fail(e) });
    this.loadTransactions();
  }

  loadTransactions() {
    this.api.transactions(this.selectedAccountId || undefined)
      .subscribe({ next: t => this.transactions = t, error: e => this.fail(e) });
  }

  createAccount() {
    this.api.createAccount(this.newAccount).subscribe({
      next: () => { this.ok('Compte créé'); this.refresh(); }, error: e => this.fail(e) });
  }

  toggleStatus(a: Account) {
    this.api.setStatus(a.id, a.status === 'ACTIVE' ? 'BLOCKED' : 'ACTIVE').subscribe({
      next: () => this.refresh(), error: e => this.fail(e) });
  }

  submitTransaction() {
    this.api.createTransaction(this.tx).subscribe({
      next: () => { this.ok('Transaction enregistrée'); this.refresh(); }, error: e => this.fail(e) });
  }

  submitTransfer() {
    this.api.transfer(this.tr).subscribe({
      next: () => { this.ok('Virement effectué'); this.refresh(); }, error: e => this.fail(e) });
  }

  send() {
    const text = this.chatInput.trim();
    if (!text || this.chatBusy) return;
    this.chatLog.push({ from: 'me', text });
    this.chatInput = '';
    this.chatBusy = true;
    this.api.chat(text, this.conversationId).subscribe({
      next: r => { this.conversationId = r.conversationId; this.chatLog.push({ from: 'bot', text: r.reply }); this.chatBusy = false; this.refresh(); },
      error: e => { this.chatLog.push({ from: 'bot', text: '⚠️ ' + this.describe(e) }); this.chatBusy = false; }
    });
  }

  private ok(m: string) { this.message = m; this.error = ''; setTimeout(() => this.message = '', 3000); }
  private fail(e: any) { this.error = this.describe(e); }
  private describe(e: any): string {
    return e?.error?.detail ?? e?.error?.message ?? e?.message ?? 'Erreur inconnue';
  }
}
