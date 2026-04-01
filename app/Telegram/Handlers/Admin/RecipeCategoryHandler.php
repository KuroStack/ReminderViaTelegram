<?php

namespace App\Telegram\Handlers\Admin;

use App\Models\RecipeCategory;
use App\Telegram\ConversationManager;
use App\Telegram\Guards;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class RecipeCategoryHandler
{
    public function __construct(private ConversationManager $conv) {}

    public function handleMenu(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $categories = RecipeCategory::all();

        $buttons = $categories->map(fn ($c) => [
            ['text' => $c->name, 'callback_data' => 'noop'],
        ])->toArray();
        $buttons[] = [['text' => '+ Add Category', 'callback_data' => 'admin:rcat:add']];
        $buttons[] = [['text' => '« Admin Menu',   'callback_data' => 'admin:menu']];

        $text = $categories->isEmpty() ? 'No recipe categories yet.' : '*Recipe Categories*';

        Telegram::editMessageText([
            'chat_id'      => $cbq->getMessage()->getChat()->getId(),
            'message_id'   => $cbq->getMessage()->getMessageId(),
            'text'         => $text,
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ]);
    }

    public function handleAddStart(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        $this->conv->setState($userId, 'arcat:enter_name');

        Telegram::editMessageText([
            'chat_id'    => $cbq->getMessage()->getChat()->getId(),
            'message_id' => $cbq->getMessage()->getMessageId(),
            'text'       => 'Enter the name for the new recipe category:',
        ]);
    }

    public function handleName(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $chatId = $msg->getChat()->getId();
        $name   = trim($msg->getText());

        try {
            RecipeCategory::create(['name' => $name]);
            $this->conv->clearState($userId);

            Telegram::sendMessage([
                'chat_id'      => $chatId,
                'text'         => "Recipe category *{$name}* created.",
                'parse_mode'   => 'Markdown',
                'reply_markup' => json_encode(Keyboards::adminMenu()),
            ]);
        } catch (\Illuminate\Database\QueryException $e) {
            Telegram::sendMessage([
                'chat_id'    => $chatId,
                'text'       => "A category named *{$name}* already exists. Enter a different name:",
                'parse_mode' => 'Markdown',
            ]);
        }
    }
}
