<?php

namespace App\Telegram\Handlers;

use App\Models\Reminder;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class ReminderHandler
{
    public function handleView(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $reminders = Reminder::active()->get();

        if ($reminders->isEmpty()) {
            $text = 'No active reminders.';
        } else {
            $lines = $reminders->map(fn ($r) =>
                "#*{$r->id}* | `{$r->cron_expression}` | Channel: `{$r->channel_id}`\n{$r->message}"
            )->join("\n\n");
            $text = "*Active Reminders*\n\n{$lines}";
        }

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => $text,
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(Keyboards::backButton()),
        ]);
    }
}
