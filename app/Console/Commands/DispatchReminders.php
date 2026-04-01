<?php

namespace App\Console\Commands;

use App\Jobs\SendReminderJob;
use App\Models\Reminder;
use Carbon\Carbon;
use Cron\CronExpression;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

class DispatchReminders extends Command
{
    protected $signature   = 'reminders:dispatch';
    protected $description = 'Fire any reminders whose cron expression is due right now';

    public function handle(): void
    {
        $timezone = config('telegram-bot.scheduler_timezone', 'UTC');
        $now      = Carbon::now($timezone);

        Reminder::active()->get()->each(function (Reminder $reminder) use ($now) {
            try {
                $cron = new CronExpression($reminder->cron_expression);
                if ($cron->isDue($now)) {
                    SendReminderJob::dispatch($reminder->channel_id, $reminder->message);
                    $this->info("Dispatched reminder #{$reminder->id}");
                }
            } catch (\Throwable $e) {
                Log::error("Invalid cron for reminder #{$reminder->id}: " . $e->getMessage());
                $this->error("Reminder #{$reminder->id} skipped: {$e->getMessage()}");
            }
        });
    }
}
