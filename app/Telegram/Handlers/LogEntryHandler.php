<?php

namespace App\Telegram\Handlers;

use App\Models\Log;
use App\Models\LogCategory;
use App\Telegram\ConversationManager;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class LogEntryHandler
{
    public function __construct(private ConversationManager $conv) {}

    public function handleStart(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $categories = LogCategory::all();

        if ($categories->isEmpty()) {
            Telegram::editMessageText([
                'chat_id'      => $chatId,
                'message_id'   => $msgId,
                'text'         => 'No log categories exist yet. Ask an admin to add one.',
                'reply_markup' => json_encode(Keyboards::backButton()),
            ]);
            return;
        }

        $buttons = $categories->map(fn ($c) => [
            ['text' => $c->name, 'callback_data' => "log:cat:{$c->id}"],
        ])->toArray();
        $buttons[] = [['text' => '« Cancel', 'callback_data' => 'main:menu']];

        $this->conv->setState($userId, 'log:select_category');

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => 'Select a category for your log entry:',
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ]);
    }

    public function handleCategorySelect(Update $update, int $catId): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $category = LogCategory::find($catId);

        $this->conv->setState($userId, 'log:enter_subject', ['cat_id' => $catId, 'cat_name' => $category?->name]);

        Telegram::editMessageText([
            'chat_id'    => $chatId,
            'message_id' => $msgId,
            'text'       => "Category: *{$category?->name}*\n\nEnter a subject line for your log entry:",
            'parse_mode' => 'Markdown',
        ]);
    }

    public function handleSubject(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();

        $subject = trim($msg->getText());
        $this->conv->mergePayload($userId, ['subject' => $subject]);
        $this->conv->setState($userId, 'log:enter_message', $this->conv->getPayload($userId));

        Telegram::sendMessage([
            'chat_id' => $chatId,
            'text'    => "Subject: *{$subject}*\n\nNow enter the details of your log entry:",
            'parse_mode' => 'Markdown',
        ]);
    }

    public function handleMessage(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();

        $payload = $this->conv->getPayload($userId);
        $logMessage = trim($msg->getText());

        Log::create([
            'category_id' => $payload['cat_id'],
            'subject'     => $payload['subject'],
            'message'     => $logMessage,
            'user_id'     => $userId,
        ]);

        $this->conv->clearState($userId);

        Telegram::sendMessage([
            'chat_id'      => $chatId,
            'text'         => "Log entry saved under *{$payload['cat_name']}*.",
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(Keyboards::mainMenu($userId)),
        ]);
    }
}
