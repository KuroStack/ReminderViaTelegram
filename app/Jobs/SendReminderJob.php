<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Telegram\Bot\Laravel\Facades\Telegram;

class SendReminderJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;

    public function __construct(
        public readonly string $channelId,
        public readonly string $message,
    ) {}

    public function handle(): void
    {
        try {
            Telegram::sendMessage([
                'chat_id'    => $this->channelId,
                'text'       => "Reminder\n\n{$this->message}",
                'parse_mode' => 'Markdown',
            ]);
        } catch (\Throwable $e) {
            Log::error("SendReminderJob failed for channel {$this->channelId}: " . $e->getMessage());
            throw $e;
        }
    }
}
