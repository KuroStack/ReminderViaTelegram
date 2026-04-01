<?php

namespace App\Telegram\Handlers\Admin;

use App\Models\Reminder;
use App\Telegram\ConversationManager;
use App\Telegram\Guards;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class ReminderAdminHandler
{
    public function __construct(private ConversationManager $conv) {}

    private function renderMenu(string $chatId, ?int $msgId): void
    {
        $reminders = Reminder::active()->get();

        $buttons = $reminders->map(fn ($r) => [
            ['text' => "#{$r->id} {$r->cron_expression} — {$r->message}", 'callback_data' => 'noop'],
            ['text' => 'Delete', 'callback_data' => "admin:rem:del:{$r->id}"],
        ])->toArray();

        $buttons[] = [['text' => '+ Add Reminder', 'callback_data' => 'admin:rem:add']];
        $buttons[] = [['text' => '« Admin Menu',   'callback_data' => 'admin:menu']];

        $text = $reminders->isEmpty() ? 'No active reminders.' : '*Active Reminders*';

        $params = [
            'chat_id'      => $chatId,
            'text'         => $text,
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ];

        if ($msgId) {
            Telegram::editMessageText(array_merge($params, ['message_id' => $msgId]));
        } else {
            Telegram::sendMessage($params);
        }
    }

    public function handleMenu(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $this->renderMenu(
            $cbq->getMessage()->getChat()->getId(),
            $cbq->getMessage()->getMessageId()
        );
    }

    public function handleAddStart(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $this->conv->setState($userId, 'arem:enter_message');

        Telegram::editMessageText([
            'chat_id'    => $cbq->getMessage()->getChat()->getId(),
            'message_id' => $cbq->getMessage()->getMessageId(),
            'text'       => 'Enter the reminder message:',
        ]);
    }

    public function handleMessage(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();

        $this->conv->mergePayload($userId, ['message' => trim($msg->getText())]);
        $this->conv->setState($userId, 'arem:enter_cron', $this->conv->getPayload($userId));

        Telegram::sendMessage([
            'chat_id' => $chatId,
            'text'    => "Enter a cron expression (5 fields: minute hour day month weekday).\n\nExamples:\n`0 9 * * 1` — every Monday 9am\n`30 18 * * 1-5` — weekdays 6:30pm\n`0 8 1 * *` — 1st of every month",
            'parse_mode' => 'Markdown',
        ]);
    }

    public function handleCron(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();
        $cron   = trim($msg->getText());

        if (count(preg_split('/\s+/', $cron)) !== 5) {
            Telegram::sendMessage([
                'chat_id' => $chatId,
                'text'    => "Invalid cron. Must have exactly 5 fields (minute hour day month weekday).\n\nTry again:",
            ]);
            return;
        }

        $this->conv->mergePayload($userId, ['cron_expression' => $cron]);
        $this->conv->setState($userId, 'arem:enter_channel', $this->conv->getPayload($userId));

        Telegram::sendMessage([
            'chat_id' => $chatId,
            'text'    => 'Enter the Telegram channel/chat ID to post reminders to:',
        ]);
    }

    public function handleChannel(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();

        $payload   = $this->conv->getPayload($userId);
        $channelId = trim($msg->getText());

        $reminder = Reminder::create([
            'message'         => $payload['message'],
            'cron_expression' => $payload['cron_expression'],
            'channel_id'      => $channelId,
        ]);

        $this->conv->clearState($userId);

        Telegram::sendMessage([
            'chat_id'    => $chatId,
            'text'       => "Reminder #{$reminder->id} created.",
            'reply_markup' => json_encode(Keyboards::adminMenu()),
        ]);
    }

    public function handleDelete(Update $update, int $reminderId): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        $reminder = Reminder::find($reminderId);
        if ($reminder) {
            $reminder->update(['active' => false]);
        }

        Telegram::answerCallbackQuery([
            'callback_query_id' => $cbq->getId(),
            'text'              => "Reminder #{$reminderId} deleted.",
        ]);

        $this->renderMenu(
            $cbq->getMessage()->getChat()->getId(),
            $cbq->getMessage()->getMessageId()
        );
    }
}
